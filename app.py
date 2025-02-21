from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kazoku.db'
app.config['SECRET_KEY'] = 'your_secret_key'  # セキュリティのため変更推奨
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# **修正①** Familyクラスを正しく定義（UserではなくFamilyを使う）
class Family(UserMixin, db.Model):
    __tablename__ = 'families'
    id = db.Column(db.Integer, primary_key=True)
    familyname = db.Column(db.String(150), unique=True, nullable=False)
    magicspell_hash = db.Column(db.String(150), nullable=False)
    member_1 = db.Column(db.String(50), nullable=False)
    member_2 = db.Column(db.String(50))
    member_3 = db.Column(db.String(50))
    member_4 = db.Column(db.String(50))
    member_5 = db.Column(db.String(50))

    def set_magicspell(self, magicspell):
        self.magicspell_hash = generate_password_hash(magicspell)

    def check_magicspell(self, magicspell):
        return check_password_hash(self.magicspell_hash, magicspell)

# **修正②** 投稿モデル
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('families.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    poster = db.Column(db.String(50), nullable=False)  # 投稿者の名前を保存

# **修正③** Flask-Login の user_loader
@login_manager.user_loader
def load_user(family_id):
    return db.session.get(Family, int(family_id))  # Family を正しく使う

# **修正④** 投稿一覧ページ（家族のメンバー一覧を取得）
@app.route('/')
@login_required
def index():
    posts = Post.query.filter_by(family_id=current_user.id).order_by(Post.timestamp.desc()).all()
    
    family = Family.query.get(current_user.id)  # Family クラスを正しく使う
    members = [family.member_1, family.member_2, family.member_3, family.member_4, family.member_5]
    members = [m for m in members if m]  # None の値を除外
    
    return render_template('index.html', posts=posts, members=members)

# **修正⑤** 登録処理（Familyを正しく使う）
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        familyname = request.form['familyname']
        magicspell = request.form['magicspell']
        member_1 = request.form['member_1']
        member_2 = request.form.get('member_2', None)
        member_3 = request.form.get('member_3', None)
        member_4 = request.form.get('member_4', None)
        member_5 = request.form.get('member_5', None)

        if Family.query.filter_by(familyname=familyname).first():
            flash('このファミリー名は既に登録されています。', 'danger')
            return redirect(url_for('register'))

        family = Family(familyname=familyname, member_1=member_1, member_2=member_2,
                        member_3=member_3, member_4=member_4, member_5=member_5)
        family.set_magicspell(magicspell)
        db.session.add(family)
        db.session.commit()
        flash('登録成功！ログインしてください。', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# **修正⑥** ログイン処理
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        familyname = request.form['familyname']
        magicspell = request.form['magicspell']
        user = Family.query.filter_by(familyname=familyname).first()

        if user and user.check_magicspell(magicspell):
            login_user(user)
            flash('ログインしました！', 'success')
            return redirect(url_for('index'))
        flash('ログイン失敗。ファミリー名またはパスワードが違います。', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('ログアウトしました。', 'success')
    return redirect(url_for('login'))

# **修正⑦** 投稿処理（誰が投稿したかを追加）
@app.route('/post', methods=['POST'])
@login_required
def post():
    content = request.form['content']
    poster = request.form['poster']  # 選択された投稿者

    new_post = Post(family_id=current_user.id, content=content, poster=poster)
    db.session.add(new_post)
    db.session.commit()
    
    flash('投稿しました！', 'success')
    return redirect(url_for('index'))

# **修正⑧** データベース初期化コマンド
@app.cli.command("init-db")
def init_db():
    db.create_all()
    print("データベースを作成しました。")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
