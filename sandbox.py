import docker
import time
import tarfile
import io
import os

class DockerSandbox:
    def __init__(self, image_name="agent-sandbox"):
        self.client = docker.from_env()
        self.container = None
        self.image_name = image_name

    def create_container(self):
        try:
            # 必要なディレクトリを事前に作成（相対パス使用）
            data_dir = "./data"
            env_file = "./.env"
            
            # 絶対パスに変換（デバッグ用）
            data_dir_abs = os.path.abspath(data_dir)
            env_file_abs = os.path.abspath(env_file)
            
            # データディレクトリの作成
            if not os.path.exists(data_dir):
                print(f"📁 データディレクトリを作成: {data_dir_abs}")
                os.makedirs(data_dir, exist_ok=True)
            else:
                print(f"✅ データディレクトリ確認済み: {data_dir_abs}")
            
            # .envファイルの存在確認
            if not os.path.exists(env_file):
                raise FileNotFoundError(f".envファイルが見つかりません: {env_file_abs}\n"
                                      f"環境変数GOOGLE_API_KEYを設定した.envファイルを作成してください")
            else:
                print(f"✅ .envファイル確認済み: {env_file_abs}")

            # コンテナを作成（ポートマッピングを追加）
            self.container = self.client.containers.run(
                self.image_name,
                command="tail -f /dev/null",  # コンテナを実行状態に保つ
                detach=True,
                tty=True,
                extra_hosts={"host.docker.internal": "host-gateway"},
                network_mode="bridge",
                ports={'7860/tcp': 7860},  # Gradioのデフォルトポート
                volumes={
                    data_dir_abs: {"bind": "/app/data", "mode": "rw"}
                }
            )

            # .envを/appにコピー
            tar_stream = io.BytesIO()
            with tarfile.open(fileobj=tar_stream, mode='w') as tar:
                tar.add(env_file, arcname='.env')
            
            tar_stream.seek(0)
            self.container.put_archive('/app/', tar_stream.read())
            print("✅ .envを/appにコピーしました")
            
            print(f"🐳 コンテナを作成しました (ID: {self.container.id[:8]}...)")
            
            # ディレクトリ構造の確認
            print("\n📋 コンテナ内ディレクトリ構造:")
            print("作業ディレクトリ:", self.exec_command("pwd"))
            print("マウントされたデータディレクトリ:", self.exec_command("ls -la /app/data/ || echo 'データディレクトリなし'"))
            print(".envファイル:", self.exec_command("ls -la /app/.env || echo '.envファイルなし'"))
        
        except Exception as e:
            raise Exception(f"コンテナ作成エラー: {e}")

    def gradio_run(self, code: str) -> None:
        if not self.container:
            self.create_container()
        
        # バックグラウンドでPythonスクリプトを実行
        self.container.exec_run(
            cmd=["python", "-c", code],
            detach=True
        )
        
        # ポート待機確認
        print("Gradioサーバーを起動中...", end="", flush=True)
        max_attempts = 10
        for attempt in range(max_attempts):
            time.sleep(1)
            print(".", end="", flush=True)
            
            # netstatを使用してポートのリスニング状態を確認
            netstat_result = self.container.exec_run(
                cmd=["bash", "-c", "netstat -tulpn 2>/dev/null | grep 7860 || echo ''"]
            )
            
            if netstat_result.output:
                print(" 完了!")
                print("\n✅ Gradioアプリが起動しました")
                print("📊 http://localhost:7860 でアクセスできます")
                return None
        
        print("\n❌ サーバー起動に失敗しました")
        return None
    
    def _safe_decode(self, data, encoding='utf-8', errors='strict'):
        """バイト列か文字列かを判断して適切に処理する"""
        if isinstance(data, bytes):
            return data.decode(encoding, errors=errors)
        return data
            
    def cleanup(self):
        if self.container:
            try:
                self.container.stop()
                self.container.remove()
                print("Container stopped and removed successfully")
            except Exception as e:
                print(f"エラー: {e}")
            finally:
                self.container = None
    
    def get_logs(self):
        """コンテナ内のプロセス状態とログを取得"""
        if not self.container:
            return "コンテナが起動していません"
            
        # プロセス確認
        ps_cmd = "ps aux | grep python | grep -v grep"
        ps_result = self.container.exec_run(cmd=["bash", "-c", ps_cmd])
        ps_output = self._safe_decode(ps_result.output).strip()
        
        # ポート確認
        port_cmd = "netstat -tulpn 2>/dev/null | grep 7860 || echo 'ポートが開いていません'"
        port_result = self.container.exec_run(cmd=["bash", "-c", port_cmd])
        port_output = self._safe_decode(port_result.output).strip()
        
        return f"プロセス状態:\n{ps_output}\n\nポート状態:\n{port_output}"
        
    def exec_command(self, command):
        """コンテナ内でコマンドを実行"""
        if not self.container:
            return "コンテナが起動していません"
        
        result = self.container.exec_run(cmd=["bash", "-c", command])
        return self._safe_decode(result.output, errors='ignore')
