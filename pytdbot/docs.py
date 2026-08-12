"""CLI: ``python -m pytdbot.docs`` / ``pytdbot-docs``."""

from __future__ import annotations

import argparse
import json
import sys

from pytdbot.ai.lookup import get_lookup


def _print_json(data: object) -> None:
    json.dump(data, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")


def cmd_stats(_: argparse.Namespace) -> int:
    _print_json(get_lookup().stats())
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    lookup = get_lookup()
    kinds = args.kind
    results = lookup.search(args.query, kinds=kinds, limit=args.limit)
    if args.json:
        _print_json(results)
    else:
        if not results:
            print(f"No results for {args.query!r}")
            return 1
        for r in results:
            kind = r.get("kind")
            name = r.get("name")
            on = r.get("on")
            label = f"{on}.{name}" if on else name
            desc = (r.get("description") or "").replace("\n", " ")
            if len(desc) > 100:
                desc = desc[:97] + "..."
            print(f"[{kind:8}] {label:40} {desc}")
    return 0


def cmd_function(args: argparse.Namespace) -> int:
    lookup = get_lookup()
    entity = lookup.get_function(args.name)
    if not entity:
        print(f"Function not found: {args.name}", file=sys.stderr)
        return 1
    if args.json:
        _print_json(entity)
    else:
        print(lookup.format_entity(entity))
    return 0


def cmd_type(args: argparse.Namespace) -> int:
    lookup = get_lookup()
    entity = lookup.get_type(args.name)
    if not entity:
        print(f"Type not found: {args.name}", file=sys.stderr)
        return 1
    if args.json:
        _print_json(entity)
    else:
        print(lookup.format_entity(entity))
    return 0


def cmd_class(args: argparse.Namespace) -> int:
    lookup = get_lookup()
    entity = lookup.get_class(args.name)
    if not entity:
        print(f"Class not found: {args.name}", file=sys.stderr)
        return 1
    if args.json:
        _print_json(entity)
    else:
        print(lookup.format_entity(entity))
    return 0


def cmd_update(args: argparse.Namespace) -> int:
    lookup = get_lookup()
    entity = lookup.get_update(args.name)
    if not entity:
        print(f"Update not found: {args.name}", file=sys.stderr)
        return 1
    if args.json:
        _print_json(entity)
    else:
        print(lookup.format_entity(entity))
    return 0


def cmd_helper(args: argparse.Namespace) -> int:
    lookup = get_lookup()
    if args.name:
        matches = lookup.get_helper(args.name)
        if not matches:
            # fall back to search
            matches = [
                h
                for h in lookup.helpers
                if args.name.lower() in h["name"].lower()
                or args.name.lower() in (h.get("on") or "").lower()
            ]
        if not matches:
            print(f"Helper not found: {args.name}", file=sys.stderr)
            return 1
        if args.json:
            _print_json(matches if len(matches) > 1 else matches[0])
        else:
            for i, h in enumerate(matches):
                if i:
                    print("\n---\n")
                print(lookup.format_helper(h))
        return 0

    # list / search helpers
    if args.query:
        results = lookup.search_helpers(args.query, limit=args.limit)
        if args.json:
            _print_json(results)
        else:
            for r in results:
                print(
                    f"{r.get('on', '?')}.{r['name']:30} {r.get('description', '')[:80]}"
                )
        return 0 if results else 1

    # list all
    if args.json:
        _print_json(lookup.helpers)
    else:
        for h in lookup.helpers:
            print(f"[{h.get('kind', '?'):14}] {h.get('on', '?'):28} {h['name']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pytdbot-docs",
        description="Look up TDLib methods/types and Pytdbot helpers",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Machine-readable JSON output",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_stats = sub.add_parser("stats", help="Show API surface counts")
    p_stats.set_defaults(func=cmd_stats)

    p_search = sub.add_parser("search", help="Search functions, types, classes, updates, helpers")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument(
        "--kind",
        action="append",
        choices=["function", "type", "class", "update", "helper"],
        help="Limit to kind (repeatable)",
    )
    p_search.add_argument("--limit", type=int, default=20)
    p_search.set_defaults(func=cmd_search)

    p_fn = sub.add_parser("function", aliases=["fn"], help="Show a TDLib function")
    p_fn.add_argument("name", help="Function name, e.g. sendMessage")
    p_fn.set_defaults(func=cmd_function)

    p_ty = sub.add_parser("type", help="Show a TDLib type")
    p_ty.add_argument("name", help="Type name, e.g. inputMessagePhoto")
    p_ty.set_defaults(func=cmd_type)

    p_cl = sub.add_parser("class", help="Show a TDLib abstract class")
    p_cl.add_argument("name", help="Class name, e.g. InputFile")
    p_cl.set_defaults(func=cmd_class)

    p_up = sub.add_parser("update", help="Show a TDLib update")
    p_up.add_argument("name", help="Update name, e.g. updateNewMessage")
    p_up.set_defaults(func=cmd_update)

    p_help = sub.add_parser("helper", help="Show or list Pytdbot helpers / bound methods")
    p_help.add_argument(
        "name",
        nargs="?",
        help="Helper name (e.g. reply_text or Message.reply_text)",
    )
    p_help.add_argument("-q", "--query", help="Search helpers")
    p_help.add_argument("--limit", type=int, default=30)
    p_help.set_defaults(func=cmd_helper)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
