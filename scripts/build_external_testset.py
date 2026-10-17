"""Constrói o conjunto de teste externo congelado da Fase 18 (ADR-051).

O conjunto reúne alegações sobre vacinação humana checadas por agências de
fact-checking e publicadas em datasets públicos. Nenhuma inferência do ImmunoCheck
(pipeline, LLM ou embeddings) é executada aqui: o script apenas baixa versões
fixadas das fontes, filtra, mapeia rótulos por regra e grava os artefatos.

Política de redistribuição:
- fontes com licença explícita para os dados (MIT) entram por completo em
  ``items.jsonl``;
- fontes cujos dados não têm licença de redistribuição entram apenas como
  referências (URL da checagem, chave e sha256 da alegação) em
  ``supplement_manifest.jsonl``. O texto é reconstruído localmente em
  ``output/external_v6/items_supplement.jsonl`` (não versionado) e conferido
  pelos hashes.

Uso:
    python scripts/build_external_testset.py            # reconstrói e confere
    python scripts/build_external_testset.py --write    # regrava os artefatos
    python scripts/build_external_testset.py --write --freeze
"""

from __future__ import annotations

import argparse
import csv
import difflib
import hashlib
import io
import json
import re
import unicodedata
import urllib.request
from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import unquote, urlparse

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "evaluation" / "refinement_v6" / "external"
CACHE_DIR = PROJECT_ROOT / "output" / "external_v6" / "raw"
SUPPLEMENT_PATH = PROJECT_ROOT / "output" / "external_v6" / "items_supplement.jsonl"
CATALOG_PATH = PROJECT_ROOT / "corpus" / "catalog.csv"
LOCAL_MANIFEST_PATH = PROJECT_ROOT / "corpus" / "processed" / "manifest.json"
EVALUATION_DIR = PROJECT_ROOT / "evaluation"

BUILT_AT = "2026-10-16"
MAX_CLAIM_CHARS = 280
MIN_CLAIM_CHARS = 25
TARGET_TOTAL = 150
# Limiares lexicais conservadores (pré-fixados antes de olhar o resultado final).
EVAL_JACCARD = 0.6
EVAL_RATIO = 0.8
INTERNAL_JACCARD = 0.7
INTERNAL_RATIO = 0.85

SUPPORTED = "SUPPORTED"
REFUTED = "REFUTED"
MISLEADING = "MISLEADING"


@dataclass(frozen=True)
class Source:
    name: str
    repository: str
    commit: str
    license: str
    redistributable: bool
    files: tuple[str, ...]

    def raw_url(self, path: str) -> str:
        return f"https://raw.githubusercontent.com/{self.repository}/{self.commit}/{path}"


SOURCES: tuple[Source, ...] = (
    Source(
        name="factckbr",
        repository="jghm-f/FACTCK.BR",
        commit="57e25d742ea14cb912069d3f6e9a0333477bc9c3",
        license="MIT",
        redistributable=True,
        files=("FACTCKBR.tsv",),
    ),
    Source(
        name="xfact",
        repository="utahnlp/x-fact",
        commit="c58b1ea78753977528485469428ff356a4b837e4",
        license="MIT",
        redistributable=True,
        files=tuple(
            f"data/x-fact/{name}"
            for name in ("train.all.tsv", "dev.all.tsv", "test.all.tsv", "ood.tsv")
        ),
    ),
    Source(
        name="factckbr_extended",
        repository="Residencia-em-IA-Grupo-6/FACTCK.BR-extended",
        commit="b19074ecff459e8b893f5e6333fc52078213e31c",
        license="código MIT; dados pertencem às agências (sem licença de redistribuição)",
        redistributable=False,
        files=("datasets/FACTCKBR_updated.tsv",),
    ),
)
SOURCE_PRIORITY = {source.name: index for index, source in enumerate(SOURCES)}

# Domínios de agências de checagem presentes nas fontes (para a restrição do AGENTS.md).
FACT_CHECKER_DOMAINS = (
    "aosfatos.org",
    "piaui.folha.uol.com.br",
    "lupa.uol.com.br",
    "lupa.news",
    "apublica.org",
    "observador.pt",
    "poligrafo.sapo.pt",
    "checamos.afp.com",
    "factcheck.afp.com",
    "projetocomprova.com.br",
    "estadao.com.br",
    "noticias.uol.com.br",
    "bol.uol.com.br",
    "boatos.org",
    "e-farsas.com",
    "oglobo.globo.com",
    "g1.globo.com",
    "agenciatatu.com.br",
    "nexojornal.com.br",
    "folha.uol.com.br",
)

# --- mapeamento de rótulos -------------------------------------------------------

XFACT_LABELS = {
    "true": SUPPORTED,
    "mostly true": SUPPORTED,
    "partly true/misleading": MISLEADING,
    "mostly false": REFUTED,
    "false": REFUTED,
    # "complicated/hard to categorise" e "other": descartados.
}

# Rótulos textuais das agências brasileiras/portuguesas (após normalização).
AGENCY_LABELS = {
    "verdadeiro": SUPPORTED,
    "verdadeiro, mas": SUPPORTED,
    "falso": REFUTED,
    "errado": REFUTED,
    "fake": REFUTED,
    "enganoso": MISLEADING,
    "enganador": MISLEADING,
    "exagerado": MISLEADING,
    "distorcido": MISLEADING,
    "sem contexto": MISLEADING,
    "fora de contexto": MISLEADING,
    "subestimado": MISLEADING,
    "impreciso": MISLEADING,
    "nao e bem assim": MISLEADING,
    # Descartados (sem correspondência adequada): insustentável, impossível provar,
    # discutível, ainda é cedo para dizer, de olho, contextualizando, outros.
}
# Rótulos que vêm como frase ("ENGANOSO: ...", "É FALSO que ...", "São FALSAS ...").
SENTENCE_LABEL_PATTERNS = (
    (re.compile(r"^(e |sao )?(falso|falsa|falsos|falsas)\b"), REFUTED),
    (re.compile(r"^(e |sao )?(enganoso|enganosa|enganosos|enganosas)\b"), MISLEADING),
)


def normalize_text(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.casefold())
    stripped = "".join(char for char in decomposed if not unicodedata.combining(char))
    return " ".join(re.sub(r"[^\w\s,]", " ", stripped).replace("_", " ").split())


def map_xfact_label(label: str) -> str | None:
    return XFACT_LABELS.get(label.strip().casefold())


def map_agency_label(label: str) -> str | None:
    normalized = normalize_text(label).strip(" ,")
    if normalized in AGENCY_LABELS:
        return AGENCY_LABELS[normalized]
    for pattern, verdict in SENTENCE_LABEL_PATTERNS:
        if pattern.match(normalized):
            return verdict
    return None


# --- filtros ----------------------------------------------------------------------

VACCINE_PATTERN = re.compile(r"vacin|imuniza(?:cao|coes|nte|ntes|r|do|dos|da|das)\b")
ANIMAL_PATTERN = re.compile(
    r"\b(caes|cao|cachorros?|gatos?|gado|bovinos?|aftosa|animal|animais|pets?|aves|"
    r"frangos?|galinhas?|equinos?|cavalos?|veterinari\w*)\b"
)
# Alegações sobre artefatos de mídia ou sobre atores políticos não testam conhecimento
# sobre vacinação (o veredito depende de autenticidade de mídia ou de fatos políticos).
MEDIA_PATTERN = re.compile(
    r"^((em|num|numa|uma|um|o|a|os|as) )*(video|videos|foto|fotos|imagem|imagens|audio|"
    r"audios|post|posts|postagem|postagens|publicacao|montagem|print|tuite|tweet|telejornal|"
    r"reportagem|texto|mensagem|corrente|site|link|pagina|perfil|noticia|artigo)\b|"
    r"^espalhou se\b|\b(propagad\w*|difundid\w*|circula\w*|espalh\w*|partilhad\w*|"
    r"compartilhad\w*) (nas|pelas) redes sociais\b"
)
POLITICAL_PATTERN = re.compile(
    r"\b(lula|bolsonaro|doria|dilma|temer|pazuello|queiroga|haddad|moraes|stf|cpi|pt|"
    r"deputad[oa]s?|senador[a]?|vereador[a]?|prefeit[oa]|governador[a]?|eleic\w*|"
    r"eleitor\w*|eleitoral|psol|inelegivel|presidente da republica|ex presidente|biden|"
    r"trump|kamala|marcelo rebelo|antonio costa)\b"
)
# Citações truncadas pela fonte ("......") ou fragmentadas ("(...)", "[...]") não formam
# uma alegação autônoma.
TRUNCATED_PATTERN = re.compile(r"(\.\.\.|…)\s*$|\.{4,}")
FRAGMENT_PATTERN = re.compile(r"\((\.\.\.|…)\)|\[(\.\.\.|…)\]")
# Exclusões pontuais da revisão por amostragem (assistida por IA), com motivo.
MANUAL_EXCLUSIONS = {
    "xfact:train.all.tsv#281": "fragmento de fala sem sujeito identificável (não autônomo)",
    "factckbr_extended:https://projetocomprova.com.br/publica%C3%A7%C3%B5es/"
    "video-engana-ao-comparar-dois-trechos-diferentes-da-transamazonica-para-elogiar-governo-"
    "bolsonaro/": "linha da fonte associa a alegação vacinal a uma checagem sobre rodovia",
}
# A URL da checagem também revela checagens de discursos políticos cuja alegação não
# nomeia o ator (por exemplo, falas transcritas de lives ou debates).
URL_POLITICAL_PATTERN = re.compile(
    r"\b(lula|bolsonaro|doria|dilma|temer|cpi|debates?|candidat\w*|eleic\w*)\b"
)
VERDICT_LEAK_PATTERN = re.compile(
    r"^(e |sao )?(falso|falsa|falsas|falsos|enganoso|enganosa|verdadeiro|verdade)\b|"
    r"^(nao e verdade|confira|entenda|checamos|verificamos)\b"
)
INDIVIDUAL_EVENT_PATTERN = re.compile(
    r"\b(morreu|morre|faleceu|falece|infartou|morte de|obito de|paciente|jogador|"
    r"atleta|cantor[a]?|ator|atriz|apresentador[a]?|enfermeir[oa]|medico|medica|"
    r"menino|menina|bebe|mulher|homem|filho|filha|neto|neta|volunt[a-z]+)\b"
)


def is_vaccination_claim(claim: str) -> bool:
    normalized = normalize_text(claim)
    return bool(VACCINE_PATTERN.search(normalized)) and not ANIMAL_PATTERN.search(normalized)


def exclusion_reason(claim: str) -> str | None:
    normalized = normalize_text(claim)
    if not is_vaccination_claim(claim):
        return "not_human_vaccination"
    if len(claim) < MIN_CLAIM_CHARS:
        return "too_short"
    if len(claim) > MAX_CLAIM_CHARS:
        return "too_long"
    if claim.rstrip().endswith("?"):
        return "question"
    if TRUNCATED_PATTERN.search(claim):
        return "truncated"
    if len(FRAGMENT_PATTERN.findall(claim)) >= 2:
        return "fragmented_quote"
    if VERDICT_LEAK_PATTERN.search(normalized):
        return "verdict_or_review_text"
    if MEDIA_PATTERN.search(normalized):
        return "media_artifact"
    if POLITICAL_PATTERN.search(normalized):
        return "political_actor"
    return None


# --- tema e cobertura heurística ----------------------------------------------------

TOPIC_RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "composicao_e_fabricacao",
        re.compile(
            r"\b(mercurio|timerosal|aluminio|grafeno|chip|nanoparticula\w*|componentes?|"
            r"ingredientes?|substancias?|fetos?|abortad\w*|formol|formaldeido|esqualeno|"
            r"lote|lotes|fabrica\w*|insumos?|adjuvantes?|veneno)\b"
        ),
    ),
    (
        "alegacoes_causais_recorrentes",
        re.compile(
            r"\b(autismo|autista|cancer|turbocancer|infertil\w*|esteril\w*|dna|"
            r"magnet\w*|hiv|aids|microcefalia|alzheimer|genetic\w*|altera\w* o dna|"
            r"diabetes|doencas? autoimune\w*)\b"
        ),
    ),
    (
        "seguranca_e_farmacovigilancia",
        re.compile(
            r"\b(morte\w*|mortes|morre\w*|morreu|faleceu|obitos?|efeitos? (adversos?|"
            r"colatera\w*)|eventos? adversos?|reac\w*|miocardite|pericardite|trombose|"
            r"coagul\w*|avc|infart\w*|paralisia|guillain|seguranca|segura|seguras|"
            r"perigos\w*|mortal|mata|matar|letal|experimenta\w*|danos?)\b"
        ),
    ),
    (
        "contraindicacoes_e_populacoes_especiais",
        re.compile(r"\b(gestantes?|gravidas?|gravidez|idosos?|imunossuprimid\w*|alergic\w*)\b"),
    ),
    (
        "eficacia_e_imunogenicidade",
        re.compile(
            r"\b(eficacia|eficaz\w*|eficiencia|anticorpos?|imunidade|protecao|protege\w*|"
            r"imunogenicidade|funciona\w*|reinfec\w*|transmit\w*|transmissao)\b"
        ),
    ),
    (
        "epidemiologia_das_doencas",
        re.compile(r"\b(casos|surtos?|epidemia|pandemia|internac\w*|cobertura vacinal)\b"),
    ),
    (
        "normas_e_calendarios",
        re.compile(
            r"\b(obrigatori\w*|calendario|doses?|reforco|campanha\w*|sus|passaporte|"
            r"ministerio|anvisa|aprova\w*|registro|faixa etaria|idade)\b"
        ),
    ),
    (
        "comunicacao_equidade_e_etica",
        re.compile(r"\b(bill gates|conspira\w*|controle populacional|agenda|farsa|plandemia)\b"),
    ),
)
DEFAULT_TOPIC = "vacinas_especificas"

# Etiquetas de vacina/doença usadas para estimar se o corpus cobre o tema.
COVERAGE_TAGS: dict[str, re.Pattern[str]] = {
    "covid19": re.compile(
        r"covid|coronav|sars cov|pfizer|comirnaty|coronavac|sinovac|astrazeneca|oxford|"
        r"janssen|moderna|sputnik|covaxin|mrna|rna mensageiro"
    ),
    "hpv": re.compile(r"\bhpv\b|papiloma"),
    "sarampo_triplice": re.compile(r"sarampo|triplice viral|caxumba|rubeola|measles"),
    "febre_amarela": re.compile(r"febre amarela|yellow fever"),
    "influenza": re.compile(r"\bgripe\b|influenza|h1n1"),
    "poliomielite": re.compile(r"polio|paralisia infantil|gotinha"),
    "dengue": re.compile(r"dengue|qdenga|butantan dv"),
    "hepatites": re.compile(r"hepatite"),
    "bcg_tuberculose": re.compile(r"\bbcg\b|tuberculose"),
    "meningite": re.compile(r"meningite|meningoc"),
    "coqueluche_dtp": re.compile(r"coqueluche|difteria|tetano|\bdtp"),
    "varicela": re.compile(r"varicela|catapora"),
    "rotavirus": re.compile(r"rotavirus"),
    "mpox": re.compile(r"mpox|variola do macaco|monkeypox"),
    "vsr": re.compile(r"sincicial|\bvsr\b"),
    "autismo": re.compile(r"autismo|autista"),
    "hantavirus": re.compile(r"hantavirus"),
    "zika_chikungunya": re.compile(r"\bzika|chikungunya"),
    "hiv_aids": re.compile(r"\bhiv\b|\baids\b|\bsida\b"),
    "cancer_terapeutica": re.compile(r"vacina\w* (contra|para) (o )?(cancer|cancro)"),
    "ebola_malaria": re.compile(r"ebola|malaria"),
}


def classify_topic(claim: str) -> str:
    normalized = normalize_text(claim)
    for topic, pattern in TOPIC_RULES:
        if pattern.search(normalized):
            return topic
    return DEFAULT_TOPIC


def coverage_tags(text: str) -> set[str]:
    normalized = normalize_text(text)
    return {tag for tag, pattern in COVERAGE_TAGS.items() if pattern.search(normalized)}


def corpus_tags(catalog_rows: Iterable[dict[str, str]]) -> set[str]:
    tags: set[str] = set()
    for row in catalog_rows:
        text = " ".join(
            row.get(key, "") or "" for key in ("document_id", "title", "notes", "url")
        ).replace("_", " ")
        tags |= coverage_tags(text)
    return tags


def corpus_topic_coverage(claim: str, available_tags: set[str]) -> str:
    tags = coverage_tags(claim)
    if not tags:
        return "generic_vaccination"
    covered = tags & available_tags
    if covered == tags:
        return "covered"
    return "partial" if covered else "not_covered"


# --- similaridade -----------------------------------------------------------------

STOPWORDS = frozenset(
    [
        "a",
        "o",
        "as",
        "os",
        "um",
        "uma",
        "uns",
        "umas",
        "de",
        "do",
        "da",
        "dos",
        "das",
        "em",
        "no",
        "na",
        "nos",
        "nas",
        "por",
        "pelo",
        "pela",
        "pelos",
        "pelas",
        "para",
        "pra",
        "com",
        "sem",
        "que",
        "e",
        "ou",
        "se",
        "ao",
        "aos",
        "sua",
        "seu",
        "suas",
        "seus",
        "como",
        "mais",
        "ja",
        "nao",
        "foi",
        "sao",
        "ser",
        "esta",
        "este",
        "essa",
        "esse",
        "isso",
        "ha",
        "tem",
        "ter",
        "vai",
        "vao",
        "the",
    ]
)


def content_tokens(text: str) -> frozenset[str]:
    return frozenset(
        token for token in normalize_text(text).replace(",", " ").split() if token not in STOPWORDS
    )


def is_near_duplicate(left: str, right: str, *, jaccard: float, ratio: float) -> bool:
    left_tokens, right_tokens = content_tokens(left), content_tokens(right)
    if left_tokens and right_tokens:
        overlap = len(left_tokens & right_tokens) / len(left_tokens | right_tokens)
        if overlap >= jaccard:
            return True
    left_norm, right_norm = normalize_text(left), normalize_text(right)
    if left_norm == right_norm:
        return True
    return difflib.SequenceMatcher(None, left_norm, right_norm).ratio() >= ratio


def collect_evaluation_claims(root: Path, *, exclude: Path) -> list[str]:
    """Reúne o campo ``claim`` de todos os JSON/JSONL em ``evaluation/``."""
    claims: set[str] = set()

    def visit(value: object) -> None:
        if isinstance(value, dict):
            for key, inner in value.items():
                if key == "claim" and isinstance(inner, str):
                    claims.add(inner)
                else:
                    visit(inner)
        elif isinstance(value, list):
            for inner in value:
                visit(inner)

    for path in sorted(root.rglob("*.json*")):
        if exclude in path.parents or path.suffix not in (".json", ".jsonl"):
            continue
        text = path.read_text(encoding="utf-8")
        if path.suffix == ".jsonl":
            for line in text.splitlines():
                if line.strip():
                    visit(json.loads(line))
        else:
            visit(json.loads(text))
    return sorted(claims)


# --- leitura das fontes -----------------------------------------------------------


@dataclass(frozen=True)
class Candidate:
    source: str
    source_key: str
    claim: str
    source_label: str
    verdict: str | None
    agency: str
    claim_date: str | None
    review_url: str | None
    redistributable: bool


def clean_claim(text: str) -> str:
    claim = " ".join((text or "").split())
    pairs = (("'", "'"), ('"', '"'), ("“", "”"), ("‘", "’"))
    changed = True
    while changed and len(claim) > 2:
        changed = False
        for opening, closing in pairs:
            if claim.startswith(opening) and claim.endswith(closing):
                claim = claim[1:-1].strip()
                changed = True
    return claim


def read_tsv(data: bytes, *, quoting: int = csv.QUOTE_MINIMAL) -> list[dict[str, str]]:
    csv.field_size_limit(1 << 30)
    reader = csv.DictReader(io.StringIO(data.decode("utf-8")), delimiter="\t", quoting=quoting)
    return list(reader)


def agency_from_url(url: str) -> str:
    host = urlparse(url if "://" in url else "https://" + url).netloc.removeprefix("www.")
    return host or "desconhecida"


def parse_factckbr(data: bytes, *, source: str, redistributable: bool) -> list[Candidate]:
    candidates = []
    for row in read_tsv(data):
        url = (row.get("URL") or "").strip()
        claim = clean_claim(row.get("claimReviewed") or "")
        label = (row.get("alternativeName") or "").strip()
        if not url or not claim:
            continue
        candidates.append(
            Candidate(
                source=source,
                source_key=url,
                claim=claim,
                source_label=label,
                verdict=map_agency_label(label),
                agency=agency_from_url(url),
                claim_date=(row.get("datePublished") or "").strip() or None,
                review_url=url,
                redistributable=redistributable,
            )
        )
    return candidates


def parse_xfact(data: bytes, *, file_name: str) -> list[Candidate]:
    candidates = []
    rows = read_tsv(data, quoting=csv.QUOTE_NONE)
    for index, row in enumerate(rows, start=1):
        if row.get("language") != "pt":
            continue
        claim = clean_claim(row.get("claim") or "")
        label = (row.get("label") or "").strip()
        if not claim:
            continue
        candidates.append(
            Candidate(
                source="xfact",
                source_key=f"{file_name}#{index}",
                claim=claim,
                source_label=label,
                verdict=map_xfact_label(label),
                agency=row.get("site") or "desconhecida",
                claim_date=(row.get("claimDate") or row.get("reviewDate") or "").strip() or None,
                review_url=None,
                redistributable=True,
            )
        )
    return candidates


def parse_source(source: Source, files: dict[str, bytes]) -> list[Candidate]:
    candidates: list[Candidate] = []
    for source_file in source.files:
        data = files[source_file]
        if source.name == "xfact":
            candidates += parse_xfact(data, file_name=Path(source_file).name)
        else:
            candidates += parse_factckbr(
                data, source=source.name, redistributable=source.redistributable
            )
    return candidates


def fetch_source_files(source: Source, cache_dir: Path, pins: dict[str, str]) -> dict[str, bytes]:
    files = {}
    for source_file in source.files:
        target = cache_dir / source.name / source.commit / source_file
        if not target.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            with urllib.request.urlopen(source.raw_url(source_file), timeout=120) as response:
                target.write_bytes(response.read())
        data = target.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        expected = pins.get(f"{source.name}:{source_file}")
        if expected and digest != expected:
            raise RuntimeError(f"sha256 divergente para {source.name}:{source_file}")
        files[source_file] = data
    return files


# --- construção -------------------------------------------------------------------


@dataclass
class BuildReport:
    candidates_by_source: Counter[str] = field(default_factory=Counter)
    vaccine_candidates_by_source: Counter[str] = field(default_factory=Counter)
    excluded: Counter[str] = field(default_factory=Counter)
    source_labels_discarded: Counter[str] = field(default_factory=Counter)

    def as_dict(self) -> dict[str, object]:
        return {
            "candidates_by_source": dict(sorted(self.candidates_by_source.items())),
            "vaccine_candidates_by_source": dict(sorted(self.vaccine_candidates_by_source.items())),
            "excluded": dict(sorted(self.excluded.items())),
            "source_labels_discarded": dict(sorted(self.source_labels_discarded.items())),
        }


def select_candidates(
    candidates: Sequence[Candidate], evaluation_claims: Sequence[str], report: BuildReport
) -> list[Candidate]:
    for candidate in candidates:
        report.candidates_by_source[candidate.source] += 1
    pool: list[Candidate] = []
    for candidate in candidates:
        if not is_vaccination_claim(candidate.claim):
            continue
        report.vaccine_candidates_by_source[candidate.source] += 1
        reason = exclusion_reason(candidate.claim)
        if not reason and candidate.review_url:
            slug = normalize_text(unquote(urlparse(candidate.review_url).path).replace("-", " "))
            if URL_POLITICAL_PATTERN.search(slug):
                reason = "political_actor"
        if f"{candidate.source}:{candidate.source_key}" in MANUAL_EXCLUSIONS:
            reason = "manual_sample_review"
        if reason:
            report.excluded[reason] += 1
            continue
        if candidate.verdict is None:
            report.excluded["label_without_mapping"] += 1
            report.source_labels_discarded[normalize_text(candidate.source_label)[:40]] += 1
            continue
        if any(
            is_near_duplicate(candidate.claim, other, jaccard=EVAL_JACCARD, ratio=EVAL_RATIO)
            for other in evaluation_claims
        ):
            report.excluded["near_duplicate_of_existing_evaluation"] += 1
            continue
        pool.append(candidate)

    pool.sort(key=lambda item: (SOURCE_PRIORITY[item.source], item.source_key, item.claim))
    groups: list[list[Candidate]] = []
    for candidate in pool:
        for group in groups:
            if is_near_duplicate(
                candidate.claim, group[0].claim, jaccard=INTERNAL_JACCARD, ratio=INTERNAL_RATIO
            ):
                group.append(candidate)
                break
        else:
            groups.append([candidate])

    selected = []
    for group in groups:
        if len({item.verdict for item in group}) > 1:
            report.excluded["near_duplicate_label_conflict"] += len(group)
            continue
        report.excluded["near_duplicate_internal"] += len(group) - 1
        selected.append(group[0])
    return selected


def claim_sha256(claim: str) -> str:
    return hashlib.sha256(claim.encode("utf-8")).hexdigest()


def make_item(candidate: Candidate, item_id: str, available_tags: set[str]) -> dict[str, object]:
    flags = []
    if INDIVIDUAL_EVENT_PATTERN.search(normalize_text(candidate.claim)):
        flags.append("possible_individual_event")
    return {
        "schema_version": 1,
        "item_id": item_id,
        "claim": candidate.claim,
        "label": candidate.verdict,
        "topic": classify_topic(candidate.claim),
        "split": "test",
        "status": "draft",
        "atomic": False,
        "evidence_chunk_ids": [],
        "rationale": None,
        "origin_type": "external_factcheck_dataset",
        "origin_reference": f"{candidate.source}:{candidate.source_key}",
        "reviewer": None,
        "reviewed_at": None,
        "second_reviewer": None,
        "second_label": None,
        "second_reviewed_at": None,
        "adjudicator": None,
        "adjudicated_at": None,
        "notes": (
            f"Rótulo original '{candidate.source_label}' ({candidate.agency}) mapeado por regra; "
            "gabarito externo de mundo real, sem revisão humana do projeto nem evidência do corpus."
        ),
        "claim_family": f"external_{item_id}",
        "primary_label": None,
        "adjudication_basis": None,
        "external_source": candidate.source,
        "external_agency": candidate.agency,
        "external_source_label": candidate.source_label,
        "external_claim_date": candidate.claim_date,
        "external_review_url": candidate.review_url,
        "corpus_topic_coverage": corpus_topic_coverage(candidate.claim, available_tags),
        "external_flags": flags,
    }


def build(
    candidates: Sequence[Candidate],
    evaluation_claims: Sequence[str],
    catalog_rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, object]], list[dict[str, object]], BuildReport]:
    report = BuildReport()
    selected = select_candidates(candidates, evaluation_claims, report)
    available = corpus_tags(catalog_rows)
    main = [candidate for candidate in selected if candidate.redistributable]
    supplement = sample_supplement(
        [candidate for candidate in selected if not candidate.redistributable],
        room=TARGET_TOTAL - len(main),
        report=report,
    )
    main_items = [
        make_item(candidate, f"ext6-{index:04d}", available)
        for index, candidate in enumerate(main, start=1)
    ]
    supplement_items = [
        make_item(candidate, f"ext6s-{index:04d}", available)
        for index, candidate in enumerate(supplement, start=1)
    ]
    return main_items, supplement_items, report


def sample_key(candidate: Candidate) -> str:
    return hashlib.sha256(f"{candidate.source}:{candidate.source_key}".encode()).hexdigest()


def sample_supplement(
    candidates: Sequence[Candidate], *, room: int, report: BuildReport
) -> list[Candidate]:
    """Amostra determinística e estratificada para limitar o total a ``TARGET_TOTAL``.

    SUPPORTED é mantido integralmente (classe escassa); o espaço restante é dividido
    igualmente entre MISLEADING e REFUTED, com sobra para REFUTED. A ordem de sorteio
    é o sha256 da referência de origem, sem olhar o texto.
    """
    by_label: dict[str, list[Candidate]] = {}
    for candidate in candidates:
        by_label.setdefault(str(candidate.verdict), []).append(candidate)
    supported = by_label.get(SUPPORTED, [])
    remaining = max(room - len(supported), 0)
    quotas = {MISLEADING: remaining // 2, REFUTED: remaining - remaining // 2}
    chosen = {sample_key(candidate) for candidate in supported}
    for label, quota in quotas.items():
        pool = sorted(by_label.get(label, []), key=sample_key)
        chosen |= {sample_key(candidate) for candidate in pool[:quota]}
        report.excluded["sampled_out_for_size_cap"] += max(len(pool) - quota, 0)
    return [candidate for candidate in candidates if sample_key(candidate) in chosen]


def manifest_entry(item: dict[str, object]) -> dict[str, object]:
    """Referência sem o texto da alegação (fonte sem licença de redistribuição)."""
    hidden = {"claim", "notes", "external_source_label"}
    entry = {key: value for key, value in item.items() if key not in hidden}
    entry["claim_sha256"] = claim_sha256(str(item["claim"]))
    entry["claim_chars"] = len(str(item["claim"]))
    return entry


def to_jsonl(rows: Iterable[dict[str, object]]) -> str:
    return "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)


def label_counts(items: Iterable[dict[str, object]]) -> dict[str, int]:
    return dict(sorted(Counter(str(item["label"]) for item in items).items()))


# --- verificação do corpus --------------------------------------------------------


def fact_checker_hits(urls: Iterable[str]) -> list[str]:
    hits = []
    for url in urls:
        host = agency_from_url(url)
        if any(host == domain or host.endswith("." + domain) for domain in FACT_CHECKER_DOMAINS):
            hits.append(url)
    return sorted(hits)


def corpus_urls(catalog_rows: Sequence[dict[str, str]], manifest_path: Path | None) -> list[str]:
    urls = [row.get("url", "") for row in catalog_rows]
    if manifest_path and manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for document in manifest.get("documents", []):
            urls += [document.get("url") or "", document.get("final_url") or ""]
    return [url for url in urls if url]


def load_catalog(path: Path = CATALOG_PATH) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as source:
        return list(csv.DictReader(source))


# --- CLI --------------------------------------------------------------------------


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true", help="regrava os artefatos versionados")
    parser.add_argument("--freeze", action="store_true", help="regrava freeze.json")
    parser.add_argument("--cache", type=Path, default=CACHE_DIR)
    args = parser.parse_args()

    freeze_path = OUTPUT_DIR / "freeze.json"
    freeze = json.loads(freeze_path.read_text(encoding="utf-8")) if freeze_path.is_file() else {}
    pins = freeze.get("raw_sha256", {})

    candidates: list[Candidate] = []
    raw_hashes: dict[str, str] = {}
    for source in SOURCES:
        files = fetch_source_files(source, args.cache, pins)
        raw_hashes |= {
            f"{source.name}:{path}": hashlib.sha256(data).hexdigest()
            for path, data in files.items()
        }
        candidates += parse_source(source, files)

    catalog = load_catalog()
    evaluation_claims = collect_evaluation_claims(EVALUATION_DIR, exclude=OUTPUT_DIR)
    main_items, supplement_items, report = build(candidates, evaluation_claims, catalog)
    hits = fact_checker_hits(corpus_urls(catalog, LOCAL_MANIFEST_PATH))
    if hits:
        raise SystemExit("O corpus contém textos de agências de checagem: " + ", ".join(hits))

    items_text = to_jsonl(main_items)
    manifest_text = to_jsonl(manifest_entry(item) for item in supplement_items)
    supplement_text = to_jsonl(supplement_items)
    SUPPLEMENT_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUPPLEMENT_PATH.write_text(supplement_text, encoding="utf-8", newline="\n")

    summary = {
        "built_at": BUILT_AT,
        "evaluation_claims_compared": len(evaluation_claims),
        "corpus_fact_checker_url_hits": hits,
        "items": {"total": len(main_items), "labels": label_counts(main_items)},
        "supplement": {"total": len(supplement_items), "labels": label_counts(supplement_items)},
        "combined_labels": label_counts([*main_items, *supplement_items]),
        "corpus_topic_coverage": dict(
            sorted(
                Counter(
                    str(item["corpus_topic_coverage"]) for item in [*main_items, *supplement_items]
                ).items()
            )
        ),
        "topics": dict(
            sorted(Counter(str(item["topic"]) for item in [*main_items, *supplement_items]).items())
        ),
        **report.as_dict(),
    }
    summary_text = json.dumps(summary, ensure_ascii=False, indent=2) + "\n"

    outputs = {
        "items.jsonl": items_text,
        "supplement_manifest.jsonl": manifest_text,
        "build_report.json": summary_text,
    }
    if args.write:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        for name, text in outputs.items():
            (OUTPUT_DIR / name).write_text(text, encoding="utf-8", newline="\n")
    else:
        for name, text in outputs.items():
            if (OUTPUT_DIR / name).read_text(encoding="utf-8") != text:
                raise SystemExit(f"Reconstrução divergente de {name}.")

    if args.freeze:
        freeze = {
            "frozen_at": BUILT_AT,
            "phase": "Fase 18 (ADR-051) — teste externo congelado",
            "sources": [
                {
                    "name": source.name,
                    "repository": source.repository,
                    "commit": source.commit,
                    "license": source.license,
                    "redistributable": source.redistributable,
                }
                for source in SOURCES
            ],
            "raw_sha256": raw_hashes,
            "sha256": {
                "evaluation/refinement_v6/external/items.jsonl": sha256_file(
                    OUTPUT_DIR / "items.jsonl"
                ),
                "evaluation/refinement_v6/external/supplement_manifest.jsonl": sha256_file(
                    OUTPUT_DIR / "supplement_manifest.jsonl"
                ),
                "scripts/build_external_testset.py": sha256_file(Path(__file__).resolve()),
            },
            "reconstructed_supplement_sha256": hashlib.sha256(
                supplement_text.encode("utf-8")
            ).hexdigest(),
            "counts": {
                "items": summary["items"],
                "supplement": summary["supplement"],
                "combined_labels": summary["combined_labels"],
            },
        }
        freeze_path.write_text(
            json.dumps(freeze, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
    elif freeze:
        expected = freeze.get("reconstructed_supplement_sha256")
        actual = hashlib.sha256(supplement_text.encode("utf-8")).hexdigest()
        if expected and expected != actual:
            raise SystemExit("O suplemento reconstruído diverge do congelado.")

    print(json.dumps({"items": summary["items"], "supplement": summary["supplement"]}))
    print(f"Suplemento local: {SUPPLEMENT_PATH}")


if __name__ == "__main__":
    main()
