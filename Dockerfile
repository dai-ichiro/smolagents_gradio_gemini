FROM python:3.12-bullseye

# ビルド依存関係のインストール
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        python3-dev \
	# ポートのリスニング状態を確認するため（Gradioを使う時）
	net-tools && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir 'smolagents[litellm,gradio]' && \
    # クリーンアップ
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 作業ディレクトリの設定
WORKDIR /app

# デフォルトコマンド
CMD ["python", "-c", "print('Container ready')"]
