from pyngrok import ngrok
import time


ngrok.set_auth_token("2pkNe3gAKW6qHFwnTjbazzOCHmr_3qGcxeysY2uP4pyAohyQx")


# 터널 열기
public_url = ngrok.connect(8000)
print(f"ngrok 터널 URL: {public_url}")


# 프로그램 유지
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("터널 종료")
    ngrok.kill()