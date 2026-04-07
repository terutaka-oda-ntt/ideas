#!/bin/bash
# テスト実行スクリプト
# 全テストを順序立てて実行し、結果をレポート

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TEST_DIR="$SCRIPT_DIR"
REPO_DIR="$( dirname "$SCRIPT_DIR" )"

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

    if python3 "$test_script" 2>&1 | tee /tmp/test_output.txt; then
        PASSED_TESTS=$((PASSED_TESTS + 1))
        TEST_RESULTS="$TEST_RESULTS\n${GREEN}✓${NC} $test_name"
        echo -e "${GREEN}✓ 成功${NC}\n"
    else
        FAILED_TESTS=$((FAILED_TESTS + 1))
        TEST_RESULTS="$TEST_RESULTS\n${RED}✗${NC} $test_name"
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
run_test "Pre-commitフック動作確認（TC-11～TC-17）" "$TEST_DIR/test_precommit_hooks.py"

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
