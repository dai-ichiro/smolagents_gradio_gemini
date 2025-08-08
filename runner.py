from sandbox import DockerSandbox

# DockerSandboxのインスタンスを作成
sandbox = DockerSandbox(image_name="agent-sandbox")

agent_code = """
import sys
import os
from dotenv import load_dotenv
from smolagents import CodeAgent, LiteLLMModel, GradioUI

load_dotenv()
api_key = os.environ.get("GOOGLE_API_KEY")

model = LiteLLMModel(
    "gemini/gemini-2.5-flash",
    api_key=api_key
)

agent = CodeAgent(
    model=model,
    tools=[],
    additional_authorized_imports=[]
)

# エージェントの実行
GradioUI(agent).launch(server_name='0.0.0.0', server_port=7860, share=False)
"""

try:
    # エージェントコンテナに関する情報を確認
    print("\n⚙️ コンテナ環境を確認しています...")
    
    # コンテナを作成して基本的な情報を確認
    sandbox.create_container()
    
    # Pythonとパッケージの確認
    print("\nPython環境:")
    print(sandbox.exec_command("which python || which python3 || echo 'Pythonが見つかりません'"))
    print("\nPythonバージョン:")
    print(sandbox.exec_command("python --version || python3 --version || echo 'バージョン情報を取得できません'"))
    
    # 必要なパッケージの確認
    print("\n必要なパッケージ確認:")
    print(sandbox.exec_command("pip list | grep -E 'smolagents|gradio' || echo 'パッケージが見つかりません'"))
    
    # Gradioアプリを起動
    print("\n🚀 Gradioアプリを起動します...")
    sandbox.gradio_run(agent_code)
    
    # ユーザーが終了するまで待機
    print("\nアプリ実行中... Ctrl+C で終了します")
    
    while True:
        try:
            cmd = input("\n> ")
            if cmd.lower() == "exit" or cmd.lower() == "quit":
                break
            elif cmd.lower() == "status":
                print("\n" + sandbox.get_logs())
            elif cmd.lower() == "exec":
                command = input("実行するコマンド: ")
                print("\n" + sandbox.exec_command(command))
            elif cmd.lower() == "help":
                print("\nコマンド一覧:")
                print("  status - サーバー状態を確認")
                print("  exec   - コンテナ内でコマンドを実行")
                print("  exit   - アプリを終了")
                print("  help   - このヘルプを表示")
            elif cmd.strip() == "":
                pass
            else:
                print(f"不明なコマンド: {cmd}. 'help'と入力してコマンド一覧を表示")
        except KeyboardInterrupt:
            print("\n終了します...")
            break
    
except Exception as e:
    print(f"エラーが発生しました: {e}")
finally:
    # 終了処理
    sandbox.cleanup()
