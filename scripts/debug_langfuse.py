"""
Script chẩn đoán kết nối Langfuse v2 - chạy độc lập không cần server.
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

pk = os.getenv("LANGFUSE_PUBLIC_KEY")
sk = os.getenv("LANGFUSE_SECRET_KEY")
host = os.getenv("LANGFUSE_HOST") or os.getenv("LANGFUSE_BASEURL")

print("=" * 60)
print("LANGFUSE v2 DEBUG DIAGNOSTIC")
print("=" * 60)
print(f"PUBLIC_KEY  : {pk[:12]}..." if pk else "PUBLIC_KEY  : NOT SET!")
print(f"SECRET_KEY  : {sk[:12]}..." if sk else "SECRET_KEY  : NOT SET!")
print(f"HOST        : {host}")
print("=" * 60)

try:
    from langfuse.decorators import observe, langfuse_context
    print("\n[1] Import langfuse.decorators: OK ✅")

    from langfuse import Langfuse
    print("[2] Import Langfuse class: OK ✅")

    # Kiểm tra auth
    lf = Langfuse(public_key=pk, secret_key=sk, host=host)
    result = lf.auth_check()
    print(f"[3] auth_check(): {result} {'✅' if result else '❌'}")

    if not result:
        print("\n❌ Auth thất bại! Hãy kiểm tra lại API Key.")
        sys.exit(1)

    # Gửi 1 trace thực sự bằng @observe v2
    @observe(name="diagnostic-trace")
    def send_test_trace():
        langfuse_context.update_current_trace(
            name="Diagnostic Trace - nhom04_403",
            tags=["debug", "lab13", "nhom04_403"],
        )
        print("[4] @observe đang chạy... ✅")
        return "test_ok"

    result = send_test_trace()
    print(f"[5] Kết quả: {result}")

    # Flush qua client chính
    lf.flush()
    print("[6] lf.flush(): OK ✅")

    print("\n" + "=" * 60)
    print("✅ HOÀN THÀNH! Trace đã được gửi lên Langfuse.")
    print("Hãy F5 trang web Langfuse sau 10 giây.")
    print("=" * 60)

except Exception as e:
    print(f"\n❌ LỖI: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
