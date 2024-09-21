# models.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, Double, DateTime, Boolean,String,Float

db = SQLAlchemy()

#model for collection_result table
class CollectionResult(db.Model):
    __tablename__ = 'collection_result'
    
    id = Column(Integer, primary_key=True)
    createdAt = Column(DateTime)
    updatedAt = Column(DateTime)
    deletedAt = Column(DateTime, nullable=True)
    xpEarned = Column(Integer, nullable=True)
    score = Column(Integer, nullable=True)
    collectionId = Column(Integer, nullable=True)
    userId = Column(Integer, nullable=True)
    entityScheduleId = Column(Integer, nullable=True)
    groupChallengeId = Column(Integer, nullable=True)


    #For Debugging purpose
    def __repr__(self):
        return f'<CollectionResult {self.id}>'
    
    #Convert CollectionResult data to dictionary for JSON serialization.
    def to_dict(self):
        return {
            'id': self.id,
            'createdAt': self.createdAt,
            'updatedAt': self.updatedAt,
            'deletedAt': self.deletedAt,
            'xpEarned': self.xpEarned,
            'score': self.score,
            'collectionId': self.collectionId,
            'userId': self.userId,
            'entityScheduleId': self.entityScheduleId,
            'groupChallengeId': self.groupChallengeId,
        }

#model for collection table
class Collection(db.Model):
    __tablename__ = 'collection'
    
    id = Column(Integer, primary_key=True)
    createdAt = Column(DateTime)
    updatedAt = Column(DateTime)
    deletedAt = Column(DateTime, nullable=True)
    name = Column(String(255), nullable=False)
    collectionType = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    status = Column(Integer, nullable=False)
    coinPrice = Column(Integer, nullable=True)
    pbucksPrice = Column(Double, nullable=True)
    desiredReturn = Column(Float, nullable=True)
    organizationId = Column(Integer, nullable=False)
    bannerImageId = Column(Integer, nullable=True)
    quizId = Column(Integer, nullable=True)

    def __repr__(self):
        return f'<Collection {self.id} - {self.name}>'
    
    def to_json(self):
        return {
            'id': self.id,
            'createdAt': self.createdAt.isoformat() if self.createdAt else None,
            'updatedAt': self.updatedAt.isoformat() if self.updatedAt else None,
            'deletedAt': self.deletedAt.isoformat() if self.deletedAt else None,
            'name': self.name,
            'collectionType': self.collectionType,
            'description': self.description,
            'status': self.status,
            'coinPrice': self.coinPrice,
            'pbucksPrice': self.pbucksPrice,
            'desiredReturn': self.desiredReturn,
            'organizationId': self.organizationId,
            'bannerImageId': self.bannerImageId,
            'quizId': self.quizId
        }

#model for collection_to_tag tbale
class CollectionToTag(db.Model):
    __tablename__ = 'collection_to_tag'
    
    id = Column(Integer, primary_key=True)
    createdAt = Column(DateTime)
    updatedAt = Column(DateTime)
    deletedAt = Column(DateTime, nullable=True)
    collectionId = Column(Integer, nullable=False)
    tagId = Column(Integer, nullable=False)

    def __repr__(self):
        return f'<CollectionToTag {self.id}>'
    
    def to_json(self):
        return {
            'id': self.id,
            'createdAt': self.createdAt,
            'updatedAt': self.updatedAt.isoformat() if self.updatedAt else None,
            'deletedAt': self.deletedAt.isoformat() if self.deletedAt else None,
            'collectionId': self.collectionId,
            'tagId': self.tagId
        }

#model for activity_to_collection table
class ActivityToCollection(db.Model):
    __tablename__ = 'activity_to_collection'
    
    id = Column(Integer, primary_key=True)
    createdAt = Column(DateTime)
    updatedAt = Column(DateTime)
    deletedAt = Column(DateTime, nullable=True)
    time = Column(Integer, nullable=True)
    reps = Column(Integer, nullable=True)
    order = Column(Integer, nullable=False)
    activityId = Column(Integer, nullable=False)
    collectionId = Column(Integer, nullable=False)
    slideId = Column(Integer, nullable=True)

    def __repr__(self):
        return f'<ActivityToCollection {self.id}>'
    
    def to_json(self):
        return {
            'id': self.id,
            'createdAt': self.createdAt.isoformat() if self.createdAt else None,
            'updatedAt': self.updatedAt.isoformat() if self.updatedAt else None,
            'deletedAt': self.deletedAt.isoformat() if self.deletedAt else None,
            'time': self.time,
            'reps': self.reps,
            'order': self.order,
            'activityId': self.activityId,
            'collectionId': self.collectionId,
            'slideId': self.slideId
        }

#model for user_to_org table
class UserToOrg(db.Model):
    __tablename__ = 'user_to_org'
    
    id = Column(Integer, primary_key=True)
    createdAt = Column(DateTime)
    updatedAt = Column(DateTime)
    deletedAt = Column(DateTime, nullable=True)
    roleId = Column(Integer, nullable=False)
    userId = Column(Integer, nullable=False)
    orgId = Column(Integer, nullable=False)

    def __repr__(self):
        return f'<UserToOrg {self.id}>'
    
    def to_json(self):
        return {
            'id': self.id,
            'createdAt': self.createdAt.isoformat() if self.createdAt else None,
            'updatedAt': self.updatedAt.isoformat() if self.updatedAt else None,
            'deletedAt': self.deletedAt.isoformat() if self.deletedAt else None,
            'roleId': self.roleId,
            'userId': self.userId,
            'orgId': self.orgId
        }

