#!/bin/bash
# テスト実行スクリプト
# 全テストを順序立てて実行し、結果をレポート

set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TEST_DIR="$SCRIPT_DIR"
REPO_DIR="$( dirname "$( dirname "$SCRIPT_DIR" )" )"

# 色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# テスト結果格納用
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
TEST_RESULTS=""
TAP_RESULTS=""
TAP_DIAGNOSTICS=""
TEST_OUTPUT_FILE="/tmp/run_tests_output_$$.log"
RESULTS_DIR="$TEST_DIR/results"
TAP_OUTPUT_FILE="$RESULTS_DIR/run_tests.tap"

echo "=================================="
echo "テスト実行開始"
echo "=================================="
echo "リポジトリ: $REPO_DIR"
echo "テストディレクトリ: $TEST_DIR"
echo ""

# テスト実行関数
run_test() {
    local test_name=$1
    local test_script=$2

    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -e "${BLUE}[テスト $TOTAL_TESTS] $test_name${NC}"

    # set -e を維持しつつ、失敗テストでも集計継続する
    set +e
    python3 "$test_script" 2>&1 | tee "$TEST_OUTPUT_FILE"
    local test_exit=${PIPESTATUS[0]}
    set -e

    if [ $test_exit -eq 0 ]; then
        PASSED_TESTS=$((PASSED_TESTS + 1))
        TEST_RESULTS="$TEST_RESULTS\n${GREEN}✓${NC} $test_name"
        TAP_RESULTS="$TAP_RESULTS\nok $TOTAL_TESTS - $test_name"
        echo -e "${GREEN}✓ 成功${NC}\n"
    else
        FAILED_TESTS=$((FAILED_TESTS + 1))
        TEST_RESULTS="$TEST_RESULTS\n${RED}✗${NC} $test_name"
        TAP_RESULTS="$TAP_RESULTS\nnot ok $TOTAL_TESTS - $test_name"
        if [ -f "$TEST_OUTPUT_FILE" ]; then
            local failure_excerpt
            failure_excerpt=$(tail -n 5 "$TEST_OUTPUT_FILE" | sed 's/\x1b\[[0-9;]*m//g' | sed 's/^/# /')
            TAP_DIAGNOSTICS="$TAP_DIAGNOSTICS\n# --- $test_name (exit=$test_exit) ---\n$failure_excerpt"
        else
            TAP_DIAGNOSTICS="$TAP_DIAGNOSTICS\n# --- $test_name (exit=$test_exit) ---"
        fi
        echo -e "${RED}✗ 失敗${NC}\n"
    fi
}

# pyyaml のインストール確認
echo -e "${YELLOW}依存パッケージのチェック${NC}"
if ! python3 -c "import yaml" 2>/dev/null; then
    echo -e "${YELLOW}pyyaml をインストール中...${NC}"
    pip install pyyaml -q || echo "インストール失敗"
fi
echo ""

# 各テストを実行
cd "$TEST_DIR"

run_test "ファイル構造チェック" "$TEST_DIR/test_structure.py"
run_test "YAML形式チェック" "$TEST_DIR/test_yaml.py"
run_test "Markdown形式チェック" "$TEST_DIR/test_markdown.py"
run_test "セキュリティチェック" "$TEST_DIR/test_security.py"
run_test "Pre-commitフック動作確認（TC-11～TC-19）" "$TEST_DIR/test_precommit_hooks.py"

# テスト結果のサマリー
echo "=================================="
echo "テスト実行完了"
echo "=================================="
echo ""
echo -e "総テスト数: $TOTAL_TESTS"
echo -e "${GREEN}成功: $PASSED_TESTS${NC}"
echo -e "${RED}失敗: $FAILED_TESTS${NC}"
echo ""

echo -e "テスト結果:"
echo -e "$TEST_RESULTS"
echo ""

# TAPレポートの出力（機械可読）
mkdir -p "$RESULTS_DIR"
{
    echo "TAP version 13"
    echo "1..$TOTAL_TESTS"
    echo -e "$TAP_RESULTS" | sed '/^$/d'

    if [ $FAILED_TESTS -gt 0 ]; then
        echo "# Failed tests: $FAILED_TESTS"
        echo -e "$TAP_DIAGNOSTICS" | sed '/^$/d'
    fi
} > "$TAP_OUTPUT_FILE"
echo "TAPレポート出力: $TAP_OUTPUT_FILE"
echo ""

rm -f "$TEST_OUTPUT_FILE"

# 終了コード
if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}=================================="
    echo "すべてのテストに通りました！"
    echo "==================================${NC}"
    exit 0
else
    echo -e "${RED}=================================="
    echo "$FAILED_TESTS 件のテストが失敗しました"
    echo "==================================${NC}"
    exit 1
fi
