# Database Redesign for Multi-Tenancy & Scalability

## Current Issues

1. **Integer PKs**: Using auto-incrementing integers exposes business data (e.g., "we have 43 clients")
2. **No Multi-Tenancy**: Client and Event tables lack `business_id` for data isolation
3. **No Audit Trail**: No tracking of who created/modified records
4. **Weak User Interaction**: `is_read`, `is_starred` are per-event, not per-user
5. **Account Owner as String**: Should be a proper foreign key to User
6. **No Soft Deletes**: Hard deletes lose data history
7. **Limited Event Categories**: Should be more flexible/extensible

## Recommended Database Structure

### Core Entity Changes

#### 1. **Use UUIDs for All Primary Keys**
**Why**: Security, distributed systems, no data leakage
```python
# Before
id: Mapped[int] = mapped_column(primary_key=True)

# After
id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
```

#### 2. **Add Multi-Tenancy Fields to All Data Tables**
```python
# Client Model
business_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("businesses.id"), nullable=False, index=True)
created_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
assigned_to_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
deleted_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)

# Event Model
business_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("businesses.id"), nullable=False, index=True)
created_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
```

#### 3. **Separate User Interaction Table**
**Problem**: Currently `is_read` and `is_starred` are on Event, but multiple users in same business should track separately.

**Solution**: Create `EventUserInteraction` table
```python
class EventUserInteraction(Base):
    """Track user-specific interactions with events."""

    __tablename__ = "event_user_interactions"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    event_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Interaction flags
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_starred: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    starred_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    user_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Unique constraint: one interaction record per user per event
    __table_args__ = (
        Index("ix_event_user_unique", "event_id", "user_id", unique=True),
    )
```

#### 4. **Add Audit Trail Model**
```python
class AuditLog(Base):
    """Track all data changes for compliance and debugging."""

    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    business_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("businesses.id"), nullable=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    # What changed
    table_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    record_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # UUID or int as string
    action: Mapped[str] = mapped_column(String(20), nullable=False)  # "CREATE", "UPDATE", "DELETE"

    # Change details
    old_values: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    new_values: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    changed_fields: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array of field names

    # Context
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
```

#### 5. **Improve Client Model**
```python
class Client(Base):
    """Represents a client company to monitor."""

    __tablename__ = "clients"

    # Primary Key (UUID instead of int)
    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4, index=True)

    # Multi-tenancy
    business_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)

    # Basic Info
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    domain: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, index=True)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Company Details (New)
    company_size: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # "1-10", "11-50", etc.
    revenue_range: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # "$1M-$10M", etc.
    headquarters_location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    founded_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Search configuration
    search_keywords: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    monitoring_frequency: Mapped[str] = mapped_column(String(20), default="daily", nullable=False)  # "hourly", "daily", "weekly"
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_checked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Customer Success (Fixed - FK to User)
    assigned_to_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    tier: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # "Enterprise", "Mid-Market", "SMB"
    health_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0-100
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Data ownership
    created_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    # Soft delete
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    business = relationship("Business", back_populates="clients")
    assigned_to_user = relationship("User", foreign_keys=[assigned_to_user_id], back_populates="assigned_clients")
    created_by_user = relationship("User", foreign_keys=[created_by_user_id])
    events = relationship("Event", back_populates="client", cascade="all, delete-orphan")

    # Composite indexes
    __table_args__ = (
        Index("ix_clients_business_active", "business_id", "is_active"),
        Index("ix_clients_business_deleted", "business_id", "is_deleted"),
    )
```

#### 6. **Improve Event Model**
```python
class Event(Base):
    """Represents a business event for a client."""

    __tablename__ = "events"

    # Primary Key (UUID instead of int)
    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4, index=True)

    # Multi-tenancy
    business_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)
    client_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)

    # Event details
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    source: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    source_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # "news", "social", "press_release"

    # Classification
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    subcategory: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # More granular
    tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array for flexible tagging

    relevance_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.5, index=True)
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # How confident is the AI classification?

    # Dates
    event_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    discovered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Deduplication
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    duplicate_of_event_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("events.id"), nullable=True)

    # Data ownership
    created_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    # Soft delete
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    business = relationship("Business", back_populates="events")
    client = relationship("Client", back_populates="events")
    user_interactions = relationship("EventUserInteraction", back_populates="event", cascade="all, delete-orphan")
    created_by_user = relationship("User", foreign_keys=[created_by_user_id])

    # Composite indexes
    __table_args__ = (
        Index("ix_events_business_client", "business_id", "client_id"),
        Index("ix_events_business_date", "business_id", "event_date"),
        Index("ix_events_business_category", "business_id", "category"),
        Index("ix_events_business_deleted", "business_id", "is_deleted"),
        Index("ix_events_content_hash", "content_hash"),
    )
```

#### 7. **Add Tag System for Flexibility**
```python
class Tag(Base):
    """Flexible tagging system for clients and events."""

    __tablename__ = "tags"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    business_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)  # Hex color

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    created_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    __table_args__ = (
        Index("ix_tags_business_name", "business_id", "name", unique=True),
    )


class ClientTag(Base):
    """Many-to-many relationship between clients and tags."""

    __tablename__ = "client_tags"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    tag_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("tags.id", ondelete="CASCADE"), nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    created_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    __table_args__ = (
        Index("ix_client_tags_unique", "client_id", "tag_id", unique=True),
    )


class EventTag(Base):
    """Many-to-many relationship between events and tags."""

    __tablename__ = "event_tags"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    event_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    tag_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("tags.id", ondelete="CASCADE"), nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    created_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    __table_args__ = (
        Index("ix_event_tags_unique", "event_id", "tag_id", unique=True),
    )
```

#### 8. **Add Notification System**
```python
class Notification(Base):
    """User notifications for important events."""

    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    business_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Notification details
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # "high_relevance_event", "client_assigned", etc.
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    link_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Related entities
    related_event_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("events.id", ondelete="CASCADE"), nullable=True)
    related_client_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("clients.id", ondelete="CASCADE"), nullable=True)

    # Status
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    __table_args__ = (
        Index("ix_notifications_user_unread", "user_id", "is_read"),
    )
```

## Migration Strategy

### Option 1: Fresh Start (Recommended for Development)
1. **Backup current data** to CSV/JSON
2. **Delete old database** file
3. **Create all new models** with UUID PKs and multi-tenancy
4. **Run fresh migrations**
5. **Create default business** for existing data
6. **Import old data** with UUID generation

### Option 2: Phased Migration (Production-Safe)
1. **Keep old tables** (rename to `clients_old`, `events_old`)
2. **Create new tables** with UUID PKs
3. **Run data migration script** to copy and transform data
4. **Verify data integrity**
5. **Switch application** to new tables
6. **Drop old tables** after verification period

## Benefits of New Structure

1. **✅ True Multi-Tenancy**: Complete data isolation per business
2. **✅ Better Security**: UUIDs hide business metrics
3. **✅ Audit Compliance**: Full change tracking
4. **✅ User-Specific Data**: Each user tracks their own read/starred status
5. **✅ Soft Deletes**: Data recovery possible
6. **✅ Flexible Tagging**: Extensible categorization
7. **✅ Scalability**: Proper indexing for large datasets
8. **✅ Data Ownership**: Track who created/modified everything
9. **✅ Notifications**: Built-in alert system
10. **✅ Better Relationships**: Proper FKs instead of strings

## Implementation Recommendation

**Start Fresh** - Given you're in development with 43 clients and 1,557 events:
1. Export current data to JSON
2. Implement new database structure
3. Create migration script to import with proper business/user assignment
4. Test thoroughly
5. This will be cleaner than trying to patch the existing structure

Would you like me to implement this new structure?
