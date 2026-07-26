#!/usr/bin/env python3
"""Validador do pacote de design docs produzido pela skill doc-generator.

Dirigido por um perfil JSON (assets/profiles/*.json). Apenas stdlib.

Uso:
    python3 validate.py --profile <perfil.json> --out docs --repo-root . \
                        [--transcript TRANSCRICAO.md] [--quiet]

Sai com codigo 1 se qualquer criterio falhar.
"""

import argparse
import json
import os
import re
import sys
import unicodedata

# ---------------------------------------------------------------- utilidades

RESET, RED, GREEN, YELLOW = "\033[0m", "\033[31m", "\033[32m", "\033[33m"


def strip_accents(text):
    return "".join(
        c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
    )


def norm(text):
    """Normaliza para comparacao tolerante: sem acento, minusculo, espacos colapsados."""
    return re.sub(r"\s+", " ", strip_accents(text).lower()).strip()


def read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


class Report:
    def __init__(self, quiet=False):
        self.rows = []
        self.quiet = quiet

    def add(self, group, criterion, ok, detail=""):
        self.rows.append((group, criterion, ok, detail))

    def failures(self):
        return [r for r in self.rows if not r[2]]

    def render(self):
        current = None
        for group, criterion, ok, detail in self.rows:
            if group != current:
                print(f"\n{YELLOW}## {group}{RESET}")
                current = group
            mark = f"{GREEN}PASS{RESET}" if ok else f"{RED}FAIL{RESET}"
            line = f"  [{mark}] {criterion}"
            if detail and (not ok or not self.quiet):
                line += f" — {detail}"
            print(line)
        total = len(self.rows)
        bad = len(self.failures())
        print(f"\n{'-' * 60}")
        color = GREEN if bad == 0 else RED
        print(f"{color}{total - bad}/{total} criterios OK{RESET}")
        return bad


# ------------------------------------------------------------------ parsing

HEADING_RE = re.compile(r"^#{1,6}\s+(.*)$", re.MULTILINE)
CODE_FENCE_RE = re.compile(r"```")
MD_PATH_RE = re.compile(r"`([\w./\-]+\.(?:ts|js|tsx|jsx|py|go|java|rb|php|prisma|json|yml|yaml|sql|md))`")
TIMESTAMP_RE = re.compile(r"\[\d{1,2}:\d{2}\]\s*\S+")
HTTP_ROUTE_RE = re.compile(r"\b(GET|POST|PUT|PATCH|DELETE)\s+/[\w:/{}\-\.]*", re.IGNORECASE)


def headings(text):
    return [h.strip() for h in HEADING_RE.findall(text)]


def has_section(text, needle):
    n = norm(needle)
    return any(n in norm(h) for h in headings(text))


def section_body(text, needle):
    """Retorna o corpo da secao cujo heading contem `needle` (ate o proximo heading de nivel <=)."""
    n = norm(needle)
    lines = text.splitlines()
    start = level = None
    for i, line in enumerate(lines):
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if not m:
            continue
        if start is None and n in norm(m.group(2)):
            start, level = i + 1, len(m.group(1))
        elif start is not None and len(m.group(1)) <= level:
            return "\n".join(lines[start:i])
    return "\n".join(lines[start:]) if start is not None else ""


def table_rows(text):
    """Linhas de tabela markdown (exclui cabecalho e separador)."""
    rows = []
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|") or not s.endswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        rows.append(cells)
    return rows


def data_rows(text, min_cols):
    """Linhas de tabela com conteudo, descartando cabecalho e linhas vazias."""
    out = []
    seen_header = False
    for cells in table_rows(text):
        if len(cells) < min_cols:
            continue
        if not seen_header:
            seen_header = True
            continue
        if not any(c for c in cells):
            continue
        out.append(cells)
    return out


def count_list_items(text):
    return len([l for l in text.splitlines() if re.match(r"^\s*[-*]\s+\S", l)])


def count_ids(text, prefix):
    return len(set(re.findall(rf"\b{prefix}-\d+\b", text)))


# ------------------------------------------------------------------- checks


def check_prd(rep, path, cfg, text):
    g = "PRD"
    for sec in cfg.get("sections", []):
        rep.add(g, f"secao '{sec}'", has_section(text, sec))

    fr_body = section_body(text, "Requisitos funcionais")
    n_fr = max(count_ids(fr_body, "PRD-FR"), len(data_rows(fr_body, 2)), count_list_items(fr_body))
    minimum = cfg.get("min_functional_requirements", 0)
    rep.add(g, f">= {minimum} requisitos funcionais", n_fr >= minimum, f"{n_fr} encontrados")

    out_body = section_body(text, "Fora de escopo")
    n_out = max(len(data_rows(out_body, 2)), count_list_items(out_body))
    minimum = cfg.get("min_out_of_scope", 0)
    rep.add(g, f">= {minimum} itens fora de escopo", n_out >= minimum, f"{n_out} encontrados")

    risk_body = section_body(text, "Riscos")
    n_risk = max(len(data_rows(risk_body, 3)), count_ids(risk_body, "PRD-RISK"))
    minimum = cfg.get("min_risks", 0)
    has_fields = all(
        any(norm(k) in norm(risk_body) for k in [term])
        for term in ["probabilidade", "impacto", "mitiga"]
    )
    rep.add(g, f">= {minimum} riscos", n_risk >= minimum, f"{n_risk} encontrados")
    rep.add(g, "riscos com probabilidade/impacto/mitigacao", has_fields)

    if cfg.get("require_quantitative_goal"):
        goals = section_body(text, "Objetivos")
        rep.add(g, "objetivo com meta quantitativa", bool(re.search(r"\d", goals)))


def check_rfc(rep, path, cfg, text, adr_files):
    g = "RFC"
    for sec in cfg.get("sections", []):
        rep.add(g, f"secao '{sec}'", has_section(text, sec))

    head = text[:1500]
    for field in cfg.get("require_metadata", []):
        rep.add(g, f"metadado '{field}'", norm(field) in norm(head))

    alts = section_body(text, "Alternativas consideradas")
    n_alt = max(count_ids(alts, "RFC-ALT"), len([h for h in headings(alts)]))
    minimum = cfg.get("min_alternatives", 0)
    rep.add(g, f">= {minimum} alternativas", n_alt >= minimum, f"{n_alt} encontradas")
    n_trade = len(re.findall(r"trade-?off|motivou o descarte|descartad", norm(alts)))
    rep.add(g, "cada alternativa com trade-off do descarte", n_trade >= n_alt and n_alt > 0,
            f"{n_trade} mencoes para {n_alt} alternativas")

    opens = section_body(text, "Questões em aberto")
    n_open = max(count_ids(opens, "RFC-OPEN"), len(headings(opens)), count_list_items(opens))
    minimum = cfg.get("min_open_questions", 0)
    rep.add(g, f">= {minimum} questoes em aberto", n_open >= minimum, f"{n_open} encontradas")

    links = set(re.findall(r"\((?:\./)?(?:adrs/)?(ADR-\d{3}[^)]*\.md)\)", text))
    minimum = cfg.get("min_adr_links", 0)
    rep.add(g, f">= {minimum} links para ADRs", len(links) >= minimum, f"{len(links)} links")
    broken = [l for l in links if os.path.basename(l) not in adr_files]
    rep.add(g, "links de ADR apontam para arquivos existentes", not broken,
            f"quebrados: {broken}" if broken else "")


def check_fdd(rep, path, cfg, text, repo_root, error_prefix):
    g = "FDD"
    for sec in cfg.get("sections", []):
        rep.add(g, f"secao '{sec}'", has_section(text, sec))

    contracts = section_body(text, "Contratos públicos")
    routes = set(m.group(0).upper() for m in HTTP_ROUTE_RE.finditer(contracts))
    minimum = cfg.get("min_endpoints", 0)
    rep.add(g, f">= {minimum} endpoints HTTP", len(routes) >= minimum, f"{len(routes)} encontrados")
    n_json = len(CODE_FENCE_RE.findall(contracts)) // 2
    rep.add(g, "endpoints com exemplo de payload", n_json >= minimum * 2,
            f"{n_json} blocos de codigo para {len(routes)} rotas")

    if error_prefix:
        errors = section_body(text, "erros")
        codes = set(re.findall(rf"\b{re.escape(error_prefix)}[A-Z_]+\b", errors))
        rep.add(g, f"matriz de erros com prefixo {error_prefix}", len(codes) >= 3,
                f"{len(codes)} codigos")

    integ = section_body(text, "Integração com o sistema existente")
    paths = set(MD_PATH_RE.findall(integ))
    existing = {p for p in paths if os.path.exists(os.path.join(repo_root, p))}
    minimum = cfg.get("min_integration_paths", 0)
    rep.add(g, f">= {minimum} caminhos reais na integracao", len(existing) >= minimum,
            f"{len(existing)} de {len(paths)} existem")

    obs = section_body(text, "Observabilidade")
    for term in cfg.get("observability_terms", []):
        rep.add(g, f"observabilidade cita '{term}'", norm(term) in norm(obs))


def check_adrs(rep, adr_dir, cfg, repo_root):
    g = "ADRs"
    if not os.path.isdir(adr_dir):
        rep.add(g, "diretorio de ADRs existe", False, adr_dir)
        return []

    pattern = re.compile(cfg.get("filename_pattern", ".*"))
    files = sorted(f for f in os.listdir(adr_dir) if f.endswith(".md") and f.upper().startswith("ADR-"))
    lo, hi = cfg.get("min_count", 0), cfg.get("max_count", 999)
    rep.add(g, f"entre {lo} e {hi} ADRs", lo <= len(files) <= hi, f"{len(files)} arquivos")

    bad_names = [f for f in files if not pattern.match(f)]
    rep.add(g, "nomes no padrao ADR-NNN-kebab-case.md", not bad_names,
            f"fora do padrao: {bad_names}" if bad_names else "")

    numbers = sorted(int(m.group(1)) for f in files if (m := re.match(r"ADR-(\d{3})", f)))
    sequential = numbers == list(range(1, len(numbers) + 1))
    rep.add(g, "numeracao sequencial sem lacunas", sequential, str(numbers))

    with_code = 0
    for f in files:
        text = read(os.path.join(adr_dir, f)) or ""
        for sec in cfg.get("sections", []):
            rep.add(g, f"{f}: secao '{sec}'", has_section(text, sec))
        if cfg.get("require_status"):
            rep.add(g, f"{f}: status declarado", bool(re.search(r"\*\*status:?\*\*|^#+\s*status", norm(text), re.M)))
        n_lines = len(text.splitlines())
        limit = cfg.get("max_lines", 10 ** 6)
        rep.add(g, f"{f}: <= {limit} linhas", n_lines <= limit, f"{n_lines} linhas")
        if any(os.path.exists(os.path.join(repo_root, p)) for p in MD_PATH_RE.findall(text)):
            with_code += 1

    minimum = cfg.get("min_with_code_reference", 0)
    rep.add(g, f">= {minimum} ADR referencia codigo real", with_code >= minimum, f"{with_code} ADRs")
    return files


def check_tracker(rep, path, cfg, text, repo_root, transcript, all_ids):
    g = "Tracker"
    cols = cfg.get("columns", [])
    rows = data_rows(text, len(cols))
    rep.add(g, f"tabela com {len(cols)} colunas", bool(rows), f"{len(rows)} linhas de dados")
    minimum = cfg.get("min_rows", 0)
    rep.add(g, f">= {minimum} linhas", len(rows) >= minimum, f"{len(rows)} linhas")

    header = next((r for r in table_rows(text) if len(r) >= len(cols)), [])
    header_ok = all(any(norm(c) in norm(h) for h in header) for c in cols)
    rep.add(g, "cabecalho no formato exigido", header_ok, " | ".join(header))

    transcript_rows = [r for r in rows if "TRANSCRICAO" in r[4].upper()]
    code_rows = [r for r in rows if "CODIGO" in r[4].upper()]

    minimum = cfg.get("min_code_rows", 0)
    rep.add(g, f">= {minimum} linhas com fonte CODIGO", len(code_rows) >= minimum, f"{len(code_rows)} linhas")

    ratio = len(transcript_rows) / len(rows) if rows else 0
    minimum = cfg.get("min_transcript_ratio", 0)
    rep.add(g, f">= {minimum:.0%} das linhas com fonte TRANSCRICAO", ratio >= minimum, f"{ratio:.0%}")

    bad_ts = [r[0] for r in transcript_rows if not TIMESTAMP_RE.search(r[5])]
    rep.add(g, "localizacao TRANSCRICAO no formato [hh:mm] Nome", not bad_ts,
            f"invalidas: {bad_ts[:5]}" if bad_ts else "")

    if transcript:
        missing = []
        for r in transcript_rows:
            m = re.search(r"\[(\d{1,2}:\d{2})\]", r[5])
            if m and f"[{m.group(1)}]" not in transcript:
                missing.append(r[0])
        rep.add(g, "timestamps existem na transcricao", not missing,
                f"nao encontrados: {missing[:5]}" if missing else "")

    bad_paths = []
    for r in code_rows:
        for p in re.findall(r"[\w./\-]+\.\w+", r[5]):
            if not os.path.exists(os.path.join(repo_root, p.strip("`"))):
                bad_paths.append((r[0], p))
    rep.add(g, "caminhos CODIGO existem no repositorio", not bad_paths,
            f"inexistentes: {bad_paths[:5]}" if bad_paths else "")

    tracked = {r[0] for r in rows}
    missing_ids = sorted(all_ids - tracked)
    coverage = 1 - (len(missing_ids) / len(all_ids)) if all_ids else 1
    minimum = cfg.get("min_id_coverage", 0)
    rep.add(g, f"cobertura de IDs >= {minimum:.0%}", coverage >= minimum,
            f"{coverage:.0%} — ausentes: {missing_ids[:8]}" if missing_ids else f"{coverage:.0%}")


def check_readme(rep, path, cfg, text):
    g = "README"
    for sec in cfg.get("sections", []):
        rep.add(g, f"secao '{sec}'", has_section(text, sec))
    n_blocks = len(CODE_FENCE_RE.findall(text)) // 2
    minimum = cfg.get("min_code_blocks", 0)
    rep.add(g, f">= {minimum} blocos de codigo (prompts)", n_blocks >= minimum, f"{n_blocks} blocos")
    if "min_iterations" in cfg:
        body = section_body(text, "Iterações")
        n_iter = max(len(headings(body)), count_list_items(body))
        rep.add(g, f">= {cfg['min_iterations']} iteracoes descritas",
                n_iter >= cfg["min_iterations"], f"{n_iter} encontradas")


def check_global(rep, docs, repo_root, checks, quarantine):
    g = "Consistencia geral"

    if checks.get("no_unsourced_markers"):
        offenders = [p for p, t in docs.items() if "[SEM FONTE]" in t]
        rep.add(g, "nenhum marcador [SEM FONTE] remanescente", not offenders, str(offenders))

    if checks.get("verify_code_paths"):
        bad, proposed_total = [], 0
        for p, t in docs.items():
            # caminhos declarados sob uma secao de "arquivos propostos" nao precisam existir
            proposed = set()
            for h in headings(t):
                if "propost" in norm(h):
                    proposed |= set(MD_PATH_RE.findall(section_body(t, h)))
            for line in t.splitlines():
                if "propost" in norm(line):
                    proposed |= set(MD_PATH_RE.findall(line))
            proposed_total += len(proposed)
            for path in set(MD_PATH_RE.findall(t)) - proposed:
                if path.endswith(".md"):
                    continue
                if not os.path.exists(os.path.join(repo_root, path)):
                    bad.append((os.path.basename(p), path))
        detail = f"nao encontrados: {bad[:8]}" if bad else f"{proposed_total} declarados como propostos"
        rep.add(g, "caminhos de codigo citados existem ou sao declarados propostos", not bad, detail)

    terms = checks.get("forbidden_terms", [])
    hits = [(os.path.basename(p), t2) for p, t in docs.items() for t2 in terms if norm(t2) in norm(t)]
    rep.add(g, "sem linguagem vaga proibida", not hits, str(hits) if hits else "")

    if quarantine:
        requirement_docs = {p: t for p, t in docs.items() if norm("PRD") in norm(os.path.basename(p))}
        hits = []
        for p, t in requirement_docs.items():
            body = section_body(t, "Requisitos funcionais")
            for item in quarantine:
                if norm(item) in norm(body):
                    hits.append((os.path.basename(p), item))
        rep.add(g, "itens descartados/adiados nao aparecem como requisito", not hits,
                str(hits) if hits else "")


# --------------------------------------------------------------------- main

ID_RE = re.compile(r"\b((?:PRD|RFC|FDD)-[A-Z]+-\d+|ADR-\d{3})\b")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--profile", required=True, help="caminho do perfil JSON")
    ap.add_argument("--out", default="docs", help="pasta dos documentos (padrao: docs)")
    ap.add_argument("--repo-root", default=".", help="raiz do repositorio (padrao: .)")
    ap.add_argument("--transcript", help="caminho da transcricao, para validar timestamps")
    ap.add_argument("--quiet", action="store_true", help="omite detalhe dos criterios que passaram")
    args = ap.parse_args()

    profile = json.loads(read(args.profile) or "{}")
    if not profile:
        print(f"{RED}Perfil nao encontrado ou invalido: {args.profile}{RESET}")
        return 2

    docs_cfg = profile.get("documents", {})
    out, root = args.out, args.repo_root
    rep = Report(quiet=args.quiet)
    transcript = read(args.transcript) if args.transcript else None

    loaded = {}
    for key in ("prd", "rfc", "fdd", "tracker", "readme"):
        cfg = docs_cfg.get(key)
        if not cfg:
            continue
        path = os.path.normpath(os.path.join(out, cfg["path"]))
        text = read(path)
        if text is None:
            if cfg.get("required", True):
                rep.add(key.upper(), "arquivo existe", False, path)
            continue
        rep.add(key.upper(), "arquivo existe", True, path)
        loaded[path] = text

    adr_cfg = docs_cfg.get("adr", {})
    adr_dir = os.path.join(out, adr_cfg.get("dir", "adrs"))
    adr_files = check_adrs(rep, adr_dir, adr_cfg, root) if adr_cfg else []
    for f in adr_files:
        p = os.path.join(adr_dir, f)
        loaded[p] = read(p) or ""

    def find(key):
        cfg = docs_cfg.get(key)
        if not cfg:
            return None, None
        p = os.path.normpath(os.path.join(out, cfg["path"]))
        return p, loaded.get(p)

    p, t = find("prd")
    if t:
        check_prd(rep, p, docs_cfg["prd"], t)
    p, t = find("rfc")
    if t:
        check_rfc(rep, p, docs_cfg["rfc"], t, adr_files)
    p, t = find("fdd")
    if t:
        check_fdd(rep, p, docs_cfg["fdd"], t, root, profile.get("error_code_prefix"))

    all_ids = set()
    for path, text in loaded.items():
        if os.path.basename(path).upper().startswith("TRACKER"):
            continue
        all_ids |= set(ID_RE.findall(text))
    all_ids |= {f[:7] for f in adr_files}

    p, t = find("tracker")
    if t:
        check_tracker(rep, p, docs_cfg["tracker"], t, root, transcript, all_ids)
    p, t = find("readme")
    if t:
        check_readme(rep, p, docs_cfg["readme"], t)

    check_global(rep, loaded, root, profile.get("global_checks", {}), profile.get("quarantine", []))

    print(f"\n{YELLOW}Validacao — perfil '{profile.get('name')}'{RESET}")
    failures = rep.render()
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
