"""
EduAgent 自动截图脚本（修复重复截图问题）
使用 Playwright 控制浏览器自动截图所有测试页面
确保每个页面都正确导航并截取不同内容
"""
import os
import time
from playwright.sync_api import sync_playwright, expect

BASE_URL = "http://localhost:5173"
SAVE_DIR = os.path.join(os.path.dirname(__file__), "..", "screenshots")

os.makedirs(SAVE_DIR, exist_ok=True)

def take_screenshot(page, filename, delay=3):
    time.sleep(delay)
    filepath = os.path.join(SAVE_DIR, filename)
    page.screenshot(path=filepath, full_page=True)
    print(f"✓ 截图保存: {filename}")
    return filepath

def is_logged_in(page):
    try:
        page.wait_for_selector('.sidebar, .layout-container, .el-menu', timeout=3000)
        return True
    except:
        try:
            page.wait_for_selector('text="AI对话"', timeout=2000)
            return True
        except:
            return False

def login(page, username, password):
    print(f"  尝试登录: {username}")
    page.fill('input[placeholder*="用户名"]', username)
    page.fill('input[placeholder*="密码"]', password)
    page.click('button:has-text("立即登录")')
    time.sleep(3)
    
    if is_logged_in(page):
        print("  ✓ 登录成功")
        return True
    else:
        print("  ✗ 登录失败")
        return False

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, args=["--start-maximized"])
    context = browser.new_context(viewport={"width": 1920, "height": 1080})
    page = context.new_page()

    try:
        print("\n[1/10] 访问登录页面...")
        page.goto(BASE_URL)
        time.sleep(2)
        take_screenshot(page, "login.png")

        print("\n[2/10] 测试登录失败...")
        page.fill('input[placeholder*="用户名"]', "admin")
        page.fill('input[placeholder*="密码"]', "wrong_password")
        page.click('button:has-text("立即登录")')
        time.sleep(0.5)
        take_screenshot(page, "login_error.png")

        print("\n[3/10] 执行登录...")
        page.fill('input[placeholder*="用户名"]', "admin")
        page.fill('input[placeholder*="密码"]', "admin123")
        page.click('button:has-text("立即登录")')
        time.sleep(4)
        
        if not is_logged_in(page):
            raise Exception("登录失败，无法继续截图")

        print("\n[4/10] 导航到首页并截取...")
        page.goto(f"{BASE_URL}/dashboard")
        time.sleep(4)
        take_screenshot(page, "dashboard.png")

        print("\n[5/10] 访问 AI 对话页面...")
        page.goto(f"{BASE_URL}/chat")
        time.sleep(4)
        take_screenshot(page, "chat.png")

        print("\n[6/10] 访问用户画像页面...")
        page.goto(f"{BASE_URL}/user-profile")
        time.sleep(4)
        take_screenshot(page, "portrait.png")

        print("\n[7/10] 访问学习路径页面...")
        page.goto(f"{BASE_URL}/path")
        time.sleep(4)
        take_screenshot(page, "learning_path.png")

        print("\n[8/10] 访问学习资源页面...")
        page.goto(f"{BASE_URL}/resources")
        time.sleep(4)
        take_screenshot(page, "resources.png")

        print("\n[9/10] 访问个人中心页面...")
        page.goto(f"{BASE_URL}/profile")
        time.sleep(4)
        take_screenshot(page, "settings.png")

        print("\n[10/10] 访问设置页面...")
        page.goto(f"{BASE_URL}/settings")
        time.sleep(4)
        take_screenshot(page, "settings2.png")

        print(f"\n{'='*60}")
        print(f"截图完成！共 {len(os.listdir(SAVE_DIR))} 张截图")

    except Exception as e:
        print(f"\n❌ 截图过程出错: {e}")
    finally:
        browser.close()
