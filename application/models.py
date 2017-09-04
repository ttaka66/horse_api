from application import db
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime
from enum import Enum

#! インサート(アップデート)日時追加予定

class Owner(db.Model):
    __tablename__ = 'owners'
    id = db.Column(db.Integer, primary_key=True)
    owner_name = db.Column(db.String(20), unique=True, nullable=True)
    horses = db.relationship('Horse', backref='owner')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<Owner id={id} owner_name={owner_name!r}>'.format(
                id=self.id, owner_name=self.owner_name)

class Breeder(db.Model):
    __tablename__ = 'breeders'
    id = db.Column(db.Integer, primary_key=True)
    breeder_name = db.Column(db.String(20), unique=True, nullable=True)
    horses = db.relationship('Horse', backref='breeder')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<Breeder id={id} breeder_name={breeder_name!r}>'.format(
                id=self.id, breeder_name=self.breeder_name)

# class TrainingCenter(Enum):
#     miho = 1
#     rittou = 2

class Trainer(db.Model):
    __tablename__ = 'trainers'
    id = db.Column(db.Integer, primary_key=True)
    trainer_name = db.Column(db.String(20), unique=True, nullable=True)
    training_center = db.Column(db.SmallInteger) # {1: 美浦, 2: 栗東}
    # training_center = db.Column(db.Enum(TrainingCenter)) # {1: 美浦, 2: 栗東}
    horses = db.relationship('Horse', backref='trainer')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<Entry id={id} trainer_name={trainer_name!r}>'.format(
                id=self.id, trainer_name=self.trainer_name)

class Horse(db.Model):
    __tablename__ = 'horses'
    id = db.Column(db.Integer, primary_key=True)
    horse_name = db.Column(db.String(20), unique=True, nullable=True)
    birth = db.Column(db.Date)
    sex = db.Column(db.SmallInteger) # {0: 牡馬, 1: 牝馬, 2: 栗東, 3: せん馬}
    owner_id = db.Column(db.Integer, db.ForeignKey('owners.id'))
    breeder_id = db.Column(db.Integer, db.ForeignKey('breeders.id'))
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainers.id'))
    horse_races = db.relationship('Horses_races', backref='horse')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<Horse id={id} horse_name={horse_name!r}>'.format(
                id=self.id, horse_name=self.horse_name)

class Jockey(db.Model):
    __tablename__ = 'jockeys'
    id = db.Column(db.Integer, primary_key=True)
    jockey_name = db.Column(db.String(20), unique=True, nullable=True)
    training_center = db.Column(db.SmallInteger) # {1: 美浦, 2: 栗東}
    horses_races = db.relationship('Horses_races', backref='jockey')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<Jockey id={id} jockey_name={jockey_name!r}>'.format(
        id=self.id, jockey_name=self.jockey_name)

class Horses_races(db.Model):
    __tablename__ = 'horses_races'
    id = db.Column(db.Integer, primary_key=True)
    horse_id = db.Column(db.Integer, db.ForeignKey('horses.id'))
    race_id = db.Column(db.Integer, db.ForeignKey('races.id'))
    jockey_id = db.Column(db.Integer, db.ForeignKey('jockeys.id'))
    frame = db.Column(db.SmallInteger)
    number = db.Column(db.SmallInteger)
    body_weight = db.Column(db.SmallInteger)
    weight = db.Column(db.SmallInteger)
    order = db.Column(db.SmallInteger)
    favorite = db.Column(db.SmallInteger)
    odds = db.Column(db.Float)
    position = db.Column(JSON)
    finish_time = db.Column(db.Interval)
    last_time = db.Column(db.Interval)
    margin = db.Column(db.String(2))
    prize = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<Horses_races horse_id={horse_id} race_id={race_id}>'.format(
                horse_id=self.horse_id, race_id=self.race_id)

class Race(db.Model):
    __tablename__ = 'races'
    __table_args__ = (db.UniqueConstraint('race_year', 'courses_id', 'courses_count', 'courses_count_day', name='unique_idx_race'),)
    id = db.Column(db.Integer, primary_key=True)
    race_year = db.Column(db.SmallInteger)
    courses_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    courses_count = db.Column(db.SmallInteger)
    courses_count_day = db.Column(db.SmallInteger)
    day_race_number = db.Column(db.SmallInteger)
    race_name = db.Column(db.String(50))
    race_rank = db.Column(db.SmallInteger) # {1: G1, 2: G2, 3: G3, 4: open, 5: 1600万下, 6: 1000万下, 7: 500万下, 8: 未勝利 , 9: 新馬}
    race_datetime = db.Column(db.DateTime)
    track = db.Column(db.SmallInteger) # {1: 芝, 2: ダート, 3: 障害}
    distance = db.Column(db.SmallInteger)
    weather = db.Column(db.String(10))
    track_condition = db.Column(db.SmallInteger) # {1: 良, 2: 稍重, 3: 重, 4: 不良}
    rule_handicap = db.Column(db.Boolean)
    rule_mare = db.Column(db.Boolean)
    rule_age = db.Column(db.String(50))
    race_horses = db.relationship('Horses_races', backref='race')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<Race id={id} race_name={race_name!r}>'.format(
                id=self.id, race_name=self.race_name)

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(20))
    rotation = db.Column(db.SmallInteger) # {1: 右回り, 2: 左回り}
    races = db.relationship('Race', backref='course')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<Course id={id} course_name={course_name!r}>'.format(
                id=self.id, course_name=self.course_name)

def initCourse():
    course_datas = [
        {
            'id': 1,
            'course_name': '札幌',
            'rotation': 1
        },
        {
            'id': 2,
            'course_name': '函館',
            'rotation': 1
        },
        {
            'id': 3,
            'course_name': '福島',
            'rotation': 1
        },
        {
            'id': 4,
            'course_name': '新潟',
            'rotation': 2
        },
        {
            'id': 5,
            'course_name': '東京',
            'rotation': 2
        },
        {
            'id': 6,
            'course_name': '中山',
            'rotation': 1
        },
        {
            'id': 7,
            'course_name': '中京',
            'rotation': 2
        },
        {
            'id': 8,
            'course_name': '京都',
            'rotation': 1
        },
        {
            'id': 9,
            'course_name': '阪神',
            'rotation': 1
        },
        {
            'id': 10,
            'course_name': '小倉',
            'rotation': 1
        },
    ]
    for course_data in course_datas:
        course = Course(**course_data)
        db.session.add(course)
    db.session.commit()

def init():
    db.create_all()

def drop():
    db.drop_all()
