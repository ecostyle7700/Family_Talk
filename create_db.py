from app import db, app

with app.app_context():
    db.drop_all()  # 既存のテーブルを削除
    db.create_all()  # 新しいテーブルを作成
    print("データベースを再作成しました。")
