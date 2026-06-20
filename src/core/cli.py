"""
cli.py — 터미널 테스트 도구

사용법:
    python cli.py "배당요구 종기가 뭐야?"
    python cli.py "말소기준권리 설명해줘"
    python cli.py "권리분석 문제 하나 내줘"
"""

from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import router

def main():
    if len(sys.argv) < 2:
        print("사용법: python cli.py \"질문\"")
        print()
        print("예시:")
        print('  python cli.py "배당요구 종기가 뭐야?"')
        print('  python cli.py "말소기준권리란?"')
        print('  python cli.py "권리분석 문제 내줘"')
        sys.exit(1)

    question = " ".join(sys.argv[1:])
    print(f"\n💬 질문: {question}")
    print("=" * 50)

    result = router.handle(question)

    print(f"\n[라우팅: {result['route']} → {result['agent']}]")
    print()
    print(result["answer"])

    if result["sources"]:
        print("\n📚 출처:")
        for src in result["sources"]:
            print(f"  • {src}")

    if result["quiz_data"]:
        print("\n" + "─" * 50)
        print("💡 답안을 작성한 후 채점하려면:")
        case_id = result["quiz_data"]["case_id"]
        print(f'   python -c "import quiz; print(quiz.grade(\'{case_id}\', \'여기에 답안\').get(\'feedback\', \'\'))"')


if __name__ == "__main__":
    main()
