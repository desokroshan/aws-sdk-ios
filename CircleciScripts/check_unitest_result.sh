if find test_result -mindepth 1 -print -quit 2>/dev/null | grep -q .; then
    echo "unit test error log"
    exit 1
else
    echo "no unit test error log"
fi
