"""数据库检查和修复脚本"""
import os
import sys

print("=" * 60)
print("QuickForm 数据库和架构检查")
print("=" * 60)
print()

# 1. 检查环境变量
print("【1】检查 .env 配置")
print("-" * 40)
if os.path.exists('.env'):
    print("✓ .env 文件存在")
    with open('.env', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if 'PASSWORD' in line or 'SECRET_KEY' in line:
                    key = line.split('=')[0]
                    print(f"  {key}=***")
                else:
                    print(f"  {line}")
else:
    print("⚠ .env 文件不存在（将使用默认配置）")
print()

# 2. 检查数据库类型配置
print("【2】数据库配置")
print("-" * 40)
from dotenv import load_dotenv
load_dotenv()

DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'sqlite')
print(f"数据库类型: {DATABASE_TYPE}")

if DATABASE_TYPE.lower() == 'mysql':
    print("⚠ 当前配置为 MySQL")
    print(f"  MYSQL_HOST: {os.getenv('MYSQL_HOST', '未设置')}")
    print(f"  MYSQL_PORT: {os.getenv('MYSQL_PORT', '未设置')}")
    print(f"  MYSQL_DATABASE: {os.getenv('MYSQL_DATABASE', '未设置')}")
    print()
    print("【检查MySQL服务】")
    print("-" * 40)
    
    try:
        import pymysql
        print("✓ pymysql 已安装")
        
        # 尝试连接MySQL
        try:
            conn = pymysql.connect(
                host=os.getenv('MYSQL_HOST', 'localhost'),
                port=int(os.getenv('MYSQL_PORT', '3306')),
                user=os.getenv('MYSQL_USER', ''),
                password=os.getenv('MYSQL_PASSWORD', ''),
                charset='utf8mb4'
            )
            print("✓ MySQL 连接成功")
            
            # 检查数据库是否存在
            cursor = conn.cursor()
            db_name = os.getenv('MYSQL_DATABASE', 'quickform')
            cursor.execute("SHOW DATABASES")
            databases = [row[0] for row in cursor.fetchall()]
            
            if db_name in databases:
                print(f"✓ 数据库 '{db_name}' 存在")
            else:
                print(f"✗ 数据库 '{db_name}' 不存在")
                print(f"  请执行: CREATE DATABASE {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            
            cursor.close()
            conn.close()
            
        except pymysql.err.OperationalError as e:
            print(f"✗ MySQL 连接失败: {e}")
            print()
            print("【解决方案】")
            print("1. 确认MySQL服务已启动")
            print("   - Windows: 服务管理器 -> 启动 MySQL")
            print("   - 或执行: net start MySQL")
            print("2. 或切换到SQLite（推荐）")
            print("   - 修改 .env 中 DATABASE_TYPE=sqlite")
            
    except ImportError:
        print("✗ pymysql 未安装")
        print("  安装命令: pip install pymysql")
        
else:
    print("✓ 当前配置为 SQLite（推荐）")
    db_file = 'quickform.db'
    if os.path.exists(db_file):
        size = os.path.getsize(db_file) / 1024
        print(f"✓ 数据库文件存在: {db_file} ({size:.1f} KB)")
    else:
        print(f"⚠ 数据库文件不存在（首次运行时会自动创建）")

print()

# 3. 检查项目架构
print("【3】检查项目架构和导入")
print("-" * 40)

required_files = [
    'app.py',
    'blueprint.py',
    'models.py',
    'ai_service.py',
    'file_service.py',
    'report_service.py',
    'utils.py',
    'requirements.txt'
]

missing_files = []
for file in required_files:
    if os.path.exists(file):
        print(f"✓ {file}")
    else:
        print(f"✗ {file} - 缺失")
        missing_files.append(file)

if missing_files:
    print(f"\n⚠ 缺失 {len(missing_files)} 个核心文件!")
else:
    print("\n✓ 所有核心文件完整")

print()

# 4. 测试Python导入
print("【4】测试Python模块导入")
print("-" * 40)

try:
    from models import Base, User, Task, Submission, AIConfig, CertificationRequest
    print("✓ models.py 导入成功")
except Exception as e:
    print(f"✗ models.py 导入失败: {e}")

try:
    from blueprint import quickform_bp, init_quickform, SessionLocal
    print("✓ blueprint.py 导入成功")
except Exception as e:
    print(f"✗ blueprint.py 导入失败: {e}")

try:
    from ai_service import call_ai_model, generate_analysis_prompt
    print("✓ ai_service.py 导入成功")
except Exception as e:
    print(f"✗ ai_service.py 导入失败: {e}")

try:
    from file_service import save_uploaded_file, read_file_content
    print("✓ file_service.py 导入成功")
except Exception as e:
    print(f"✗ file_service.py 导入失败: {e}")

try:
    from report_service import save_analysis_report, generate_report_image
    print("✓ report_service.py 导入成功")
except Exception as e:
    print(f"✗ report_service.py 导入失败: {e}")

print()

# 5. 检查依赖
print("【5】检查Python依赖")
print("-" * 40)

required_packages = [
    'flask',
    'flask_login',
    'flask_bcrypt',
    'sqlalchemy',
    'python-dotenv',
    'pandas',
    'openpyxl',
    'matplotlib'
]

missing_packages = []
for package in required_packages:
    try:
        __import__(package.replace('-', '_'))
        print(f"✓ {package}")
    except ImportError:
        print(f"✗ {package} - 未安装")
        missing_packages.append(package)

if missing_packages:
    print(f"\n⚠ 缺失 {len(missing_packages)} 个依赖包")
    print("安装命令: pip install -r requirements.txt")
else:
    print("\n✓ 所有依赖包已安装")

print()

# 6. 总结和建议
print("=" * 60)
print("【总结和建议】")
print("=" * 60)

if DATABASE_TYPE.lower() == 'mysql':
    print()
    print("⚠ MySQL连接失败的解决方案:")
    print()
    print("方案1: 启动MySQL服务（如果已安装）")
    print("------")
    print("Windows:")
    print("  1. Win+R -> services.msc")
    print("  2. 找到 MySQL 服务")
    print("  3. 右键 -> 启动")
    print()
    print("或命令行:")
    print("  net start MySQL")
    print()
    print("方案2: 切换到SQLite（推荐）")
    print("------")
    print("1. 编辑 .env 文件，修改:")
    print("   DATABASE_TYPE=sqlite")
    print()
    print("2. 重新启动应用:")
    print("   python app.py")
    print()
    print("SQLite优点:")
    print("  - 无需安装配置")
    print("  - 开箱即用")
    print("  - 适合中小规模应用")
else:
    print()
    print("✓ 当前使用SQLite，无需额外配置")
    print()
    print("启动应用:")
    print("  python app.py")
    print()
    print("访问地址:")
    print("  http://localhost:5001/quickform")
    print()
    print("管理员账号:")
    print("  用户名: wzkjgz")
    print("  密码: wzkjgz123!")

print()
print("=" * 60)
