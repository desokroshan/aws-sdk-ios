if find integration_test_result -mindepth 1 -print -quit 2>/dev/null | grep -q .; then
    echo "integration test error log"
    exit 1
else
    echo "no integration test error log"
fi
