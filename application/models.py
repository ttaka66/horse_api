from application import db
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime

#! インサート(アップデート)日時追加予定

class Owner(db.Model):
    __tablename__ = 'owners'
    id = db.Column(db.Integer, primary_key=True)
    owner_name = db.Column(db.String(20))
    owners = db.relationship('Horse', backref='owner')

    def __repr__(self):
        return '<Owner id={id} owner_name={owner_name!r}>'.format(
                id=self.id, owner_name=self.owner_name)

class Breeder(db.Model):
    __tablename__ = 'breeders'
    id = db.Column(db.Integer, primary_key=True)
    breeder_name = db.Column(db.String(20))
    breeders = db.relationship('Horse', backref='breeder')

    def __repr__(self):
        return '<Breeder id={id} breeder_name={breeder_name!r}>'.format(
                id=self.id, breeder_name=self.breeder_name)

class Trainer(db.Model):
    __tablename__ = 'trainers'
    id = db.Column(db.Integer, primary_key=True)
    trainer_name = db.Column(db.Text)
    training_center = db.Column(db.SmallInteger)
    trainers = db.relationship('Horse', backref='trainer') # {1: 美浦, 2: 栗東}

    def __repr__(self):
        return '<Entry id={id} trainer_name={trainer_name!r}>'.format(
                id=self.id, trainer_name=self.trainer_name)

class Horse(db.Model):
    __tablename__ = 'horses'
    id = db.Column(db.Integer, primary_key=True)
    horse_name = db.Column(db.String(20))
    birth = db.Column(db.Date)
    sex = db.Column(db.SmallInteger)
    owner_id = db.Column(db.Integer, db.ForeignKey('owners.id'))
    breeder_id = db.Column(db.Integer, db.ForeignKey('breeders.id'))
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainers.id'))
    races = db.relationship('Horses_races', backref='horse')

    def __repr__(self):
        return '<Horse id={id} horse_name={horse_name!r}>'.format(
                id=self.id, horse_name=self.horse_name)

class Jockey(db.Model):
    __tablename__ = 'jockeys'
    id = db.Column(db.Integer, primary_key=True)
    jockey_name = db.Column(db.String(20))
    training_center = db.Column(db.SmallInteger) # {1: 美浦, 2: 栗東}
    horses_races = db.relationship('Horses_races', backref='jockey')

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

    def __repr__(self):
        return '<Horses_races horse_id={horse_id} race_id={race_id}>'.format(
                horse_id=self.horse_id, race_id=self.race_id)

class Race(db.Model):
    __tablename__ = 'races'
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
    weather = db.Column(db.SmallInteger)
    track_condition = db.Column(db.SmallInteger) # {1: 良, 2: 稍重, 3: 重, 4: 不良}
    rule_handicap = db.Column(db.Boolean)
    rule_mare = db.Column(db.Boolean)
    rule_age = db.Column(db.String(50))
    horses = db.relationship('Horses_races', backref='race')

    def __repr__(self):
        return '<Race id={id} race_name={race_name!r}>'.format(
                id=self.id, race_name=self.race_name)

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(20))
    rotation = db.Column(db.SmallInteger) # {1: 右回り, 2: 左回り}
    races = db.relationship('Race', backref='course')

    def __repr__(self):
        return '<Course id={id} course_name={course_name!r}>'.format(
                id=self.id, course_name=self.course_name)

def init():
    db.create_all()

def drop():
    db.drop_all()
