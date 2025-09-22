from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os
from PIL import Image
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# 캡처 저장 폴더 지정
image_files_dir = os.getenv("IMAGE_FILE_DIR")
os.makedirs(image_files_dir, exist_ok=True)

# Chrome 드라이버 세팅
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
driver = webdriver.Chrome(options=options)

# 로그인 페이지 접속
login_url = os.getenv("LOGIN_URL")  # 실제 로그인 페이지 주소로 변경 필요
# 교재 URL
url = os.getenv("PAGE_URL")

driver.get(login_url)
time.sleep(2)  # 로딩 대기

# 아이디/비밀번호 입력 & 로그인
user_id = os.getenv("USER_ID")        # 본인 계정 정보
user_pw = os.getenv("USER_PW")

driver.find_element(By.ID, 'userId').send_keys(user_id)
driver.find_element(By.ID, 'userPwd').send_keys(user_pw)

# 로그인 버튼 클릭 (클래스, id 등 실제 요소로 변경)
driver.find_element(By.CLASS_NAME, 'btn-lg').click()
time.sleep(4)  # 로그인 대기 (2차 인증, 보안문자 등 있을 경우 추가 처리 필요)

# 교재 URL
driver.get(url)
# 페이지 로딩 대기 (네트워크 환경/페이지 구조에 따라 증가 가능)
time.sleep(5)

num_pages = int(driver.find_element(By.CLASS_NAME, 'label-page').text.split('/')[1].strip())
print(f"전체 페이지 수: {num_pages}")

for i in range(num_pages):
    try:
        element_to_capture = driver.find_element(By.CLASS_NAME, "current")
        shot_path = os.path.join(image_files_dir, f"page_{i + 1}.png")
        element_to_capture.screenshot(shot_path)
        print(f"{i + 1}페이지 캡처 저장: {shot_path}")
    except Exception as e:
        print(f"캡처 요소(.background)를 찾는 데 실패했습니다: {e}")
        break

    try:
        next_btn = driver.find_element(By.CSS_SELECTOR, ".btn-side-next-page")
        next_btn.click()
        time.sleep(2)
    except Exception as e:
        if i < num_pages - 1: # 마지막 페이지가 아닌데도 버튼을 못찾으면 에러 출력
             print("다음 페이지 버튼 탐색 실패:", e)
        break

driver.quit()

# PNG 파일만 리스트로 불러오기(페이지 순서대로 정렬)
image_files = sorted(
    [os.path.join(image_files_dir, fname) for fname in os.listdir(image_files_dir) if fname.endswith(".png")],
    key=lambda f: int(os.path.splitext(os.path.basename(f))[0].split('_')[1])
)

# 이미지 리스트를 Pillow 객체로 불러오기
images = [Image.open(f).convert("RGB") for f in image_files]

if images:
    pdf_filename = f"./outputs/교재_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    images[0].save(
        pdf_filename, save_all=True, append_images=images[1:]
    )
    print(f"\n✅ 총 {len(images)}개 이미지를 PDF로 저장했습니다: {pdf_filename}")

    print("PDF 생성 완료. 캡처 이미지 파일을 삭제합니다...")
    try:
        for file_path in image_files:
            os.remove(file_path)
        print("✅ 모든 캡처 이미지를 성공적으로 삭제했습니다.")
    except Exception as e:
        print(f"❌ 파일 삭제 중 오류가 발생했습니다: {e}")

else:
    print("❌ 캡처된 PNG 이미지가 없어 PDF를 생성할 수 없습니다.")