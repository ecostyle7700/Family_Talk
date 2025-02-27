from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from flask_socketio import SocketIO, emit
from datetime import datetime
from dotenv import load_dotenv
import pytz
import os

load_dotenv()

# 日本時間のタイムゾーン設定
JST = pytz.timezone('Asia/Tokyo')

app = Flask(__name__)
socketio = SocketIO(app)  # WebSocket を有効化

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# 家族モデル
class Family(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    familyname = db.Column(db.String(150), unique=True, nullable=False)
    magicspell_hash = db.Column(db.String(256), nullable=False)# 150 → 256 に変更
    member_1 = db.Column(db.String(150), nullable=True)
    member_2 = db.Column(db.String(150), nullable=True)
    member_3 = db.Column(db.String(150), nullable=True)
    member_4 = db.Column(db.String(150), nullable=True)
    member_5 = db.Column(db.String(150), nullable=True)

    def set_magicspell(self, magicspell):
        self.magicspell_hash = generate_password_hash(magicspell)

    def check_magicspell(self, magicspell):
        return check_password_hash(self.magicspell_hash, magicspell)

# 投稿モデル
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    poster = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.current_timestamp())

# ログイン管理
@login_manager.user_loader
def load_family(family_id):
    return db.session.get(Family, int(family_id))

# ホーム（投稿一覧）
@app.route('/')
@login_required
def index():
    posts = Post.query.filter_by(family_id=current_user.id).order_by(Post.timestamp.desc()).all()
    for post in posts:
        post.timestamp = post.timestamp.replace(tzinfo=pytz.utc).astimezone(JST)
    members = [current_user.familyname, current_user.member_1, current_user.member_2, current_user.member_3, current_user.member_4, current_user.member_5]
    members = [m for m in members if m]  # Noneを除外
    return render_template('index.html', posts=posts, members=members)

# 投稿の作成（WebSocketで通知する）
@app.route('/post', methods=['POST'])
@login_required
def post():
    content = request.form['content']
    poster = request.form['poster']
    new_post = Post(family_id=current_user.id, poster=poster, content=content)
    db.session.add(new_post)
    db.session.commit()

    post_data = {
        'poster': new_post.poster,
        'content': new_post.content,
        'timestamp': new_post.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    }
    socketio.emit('new_post', post_data, broadcast=True)  # WebSocket で全員に送信
    
    flash('投稿しました！', 'success')
    return redirect(url_for('index'))

@socketio.on('connect')
def handle_connect():
    print('クライアントが接続しました')

# 投稿の削除
@app.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get(post_id)
    if post and post.family_id == current_user.id:  # 自分の投稿のみ削除
        db.session.delete(post)
        db.session.commit()
        flash('投稿を削除しました。', 'success')
    else:
        flash('削除権限がありません。', 'danger')
    return redirect(url_for('index'))

# 投稿の編集
@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get(post_id)
    if not post or post.family_id != current_user.id:
        flash('編集権限がありません。', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        post.content = request.form['content']
        db.session.commit()
        flash('投稿を更新しました。', 'success')
        return redirect(url_for('index'))

    return render_template('edit_post.html', post=post)


# 家族登録
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        familyname = request.form['familyname']
        magicspell = request.form['magicspell']
        member_1 = request.form.get("member_1")
        member_2 = request.form.get("member_2")
        member_3 = request.form.get("member_3")
        member_4 = request.form.get("member_4")
        member_5 = request.form.get("member_5")       
        
        if Family.query.filter_by(familyname=familyname).first():
            flash('この家族名は既に使われています。', 'danger')
            return redirect(url_for('register'))
        # パスワードをハッシュ化
        magicspell_hash = generate_password_hash(magicspell)

        # 新しいファミリーを作成
        new_family = Family(
            familyname=familyname,
            magicspell_hash=magicspell_hash,
            member_1=member_1,
            member_2=member_2,
            member_3=member_3,
            member_4=member_4,
            member_5=member_5,
        )
        db.session.add(new_family)
        db.session.commit()
        flash('登録成功！ログインしてください。', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# ログイン
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        familyname = request.form['familyname']
        magicspell = request.form['magicspell']
        
        family = Family.query.filter_by(familyname=familyname).first()
        if family and check_password_hash(family.magicspell_hash, magicspell):
            login_user(family)
            flash('ログインしました！', 'success')
            return redirect(url_for('index'))
        flash('ログイン失敗。ファミリー名またはパスワードが違います。', 'danger')

    return render_template('login.html')

# ログアウト
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('ログアウトしました。', 'success')
    return redirect(url_for('login'))

# 新しいメッセージを受信したときの処理
@socketio.on("new_message")
def handle_new_message(data):
    new_post = Post(family_id=current_user.id, poster=data["poster"], content=data["content"])
    db.session.add(new_post)
    db.session.commit()

    # 送信データにタイムスタンプを追加
    data["timestamp"] = new_post.timestamp.strftime('%Y.%m.%d %H:%M')

    # 全クライアントに新しいメッセージをブロードキャスト
    emit("receive_message", data, broadcast=True)

# データベース初期化用（初回実行時のみ）
@app.cli.command("init-db")
def init_db():
    db.create_all()
    print("データベースを作成しました。")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))  # Render の環境変数 PORT を取得、なければ 5000 を使用
    app.run(host="0.0.0.0", port=port, debug=True)  # 1回だけ実行

