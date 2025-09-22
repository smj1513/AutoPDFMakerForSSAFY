from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os
from PIL import Image
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# 캡처 저장 폴더 지정
image_files_dir = os.getenv("IMAGE_FILE_DIR") # 경로 구분자를 \\로 사용하거나 r"E:\captures"와 같이 사용하는 것이 안전합니다.
os.makedirs(image_files_dir, exist_ok=True)

# 1. Chrome 드라이버 세팅
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
driver = webdriver.Chrome(options=options)

# 2. 로그인 페이지 접속
login_url = os.getenv("LOGIN_URL")  # 실제 로그인 페이지 주소로 변경 필요
# 교재 URL
url = os.getenv("PAGE_URL")

driver.get(login_url)
time.sleep(2)  # 로딩 대기

# 3. 아이디/비밀번호 입력 & 로그인
user_id = os.getenv("USER_ID")        # 본인 계정 정보
user_pw = os.getenv("USER_PW")

# 실제 입력 박스의 name/id/class를 F12로 확인해 아래와 같이 셀렉터 수정
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
    # 'background' 클래스를 가진 요소를 찾아 캡처합니다.
    try:
        element_to_capture = driver.find_element(By.CLASS_NAME, "current")
        # 찾은 요소의 스크린샷을 저장합니다.
        shot_path = os.path.join(image_files_dir, f"page_{i + 1}.png")
        element_to_capture.screenshot(shot_path)
        print(f"{i + 1}페이지 캡처 저장: {shot_path}")
    except Exception as e:
        print(f"캡처 요소(.background)를 찾는 데 실패했습니다: {e}")
        break

    # 다음 페이지 이동 - 실제 오른쪽 화살표 버튼의 selector로 수정!
    try:
        next_btn = driver.find_element(By.CSS_SELECTOR, ".btn-side-next-page")  # 예시
        next_btn.click()
        time.sleep(2)  # 페이지 전환 대기
    except Exception as e:
        if i < num_pages - 1: # 마지막 페이지가 아닌데도 버튼을 못찾으면 에러 출력
             print("다음 페이지 버튼 탐색 실패:", e)
        break

driver.quit()

# PNG 파일만 리스트로 불러오기(페이지 순서대로 정렬)
# 파일 이름을 숫자로 변환하여 정렬해야 1, 2, ... 10, 11 순서를 보장할 수 있습니다.
image_files = sorted(
    [os.path.join(image_files_dir, fname) for fname in os.listdir(image_files_dir) if fname.endswith(".png")],
    key=lambda f: int(os.path.splitext(os.path.basename(f))[0].split('_')[1])
)

# 이미지 리스트를 Pillow 객체로 불러오기
images = [Image.open(f).convert("RGB") for f in image_files]

# 첫 이미지를 기준으로, 나머지는 append_pages로 PDF 생성
if images:
    # PDF 파일 이름을 현재 시간으로 설정
    pdf_filename = f"./outputs/교재_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    images[0].save(
        pdf_filename, save_all=True, append_images=images[1:]
    )
    print(f"\n✅ 총 {len(images)}개 이미지를 PDF로 저장했습니다: {pdf_filename}")

    ### 추가된 부분 시작 ###
    print("PDF 생성 완료. 캡처 이미지 파일을 삭제합니다...")
    try:
        for file_path in image_files:
            os.remove(file_path)
        # 모든 파일 삭제 후 폴더도 삭제하고 싶다면 아래 주석 해제
        # os.rmdir(image_files_dir)
        print("✅ 모든 캡처 이미지를 성공적으로 삭제했습니다.")
    except Exception as e:
        print(f"❌ 파일 삭제 중 오류가 발생했습니다: {e}")
    ### 추가된 부분 끝 ###

else:
    print("❌ 캡처된 PNG 이미지가 없어 PDF를 생성할 수 없습니다.")