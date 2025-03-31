from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Recommendation(Base):
    __tablename__ = 'user_recommendations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer, nullable=False)
    collectionId = Column(Integer, nullable=False)
    collectionType = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    name = Column(String(255), nullable=False)
    organizationId = Column(Integer, nullable=False)
    createdAt = Column(TIMESTAMP, nullable=False)

    def __repr__(self):
        return f"<Recommendation(id={self.id}, userId={self.userId}, collectionId={self.collectionId},collectionType={self.collectionType},description={self.description},name={self.name},organizationId={self.organizationId},createdAt={self.createdAt})>"
