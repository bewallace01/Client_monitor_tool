# Database Migration - Status Column Fix

## Issue
When accessing the Database page, you received an error:
```
sqlite3.OperationalError: no such column: status
```

## Cause
The existing database was created with the old SQLAlchemy schema (from Phase 1) which didn't include a `status` column in the events table. The new SQLite storage layer expects this column for event workflow tracking (new → reviewed → actioned → archived).

## Solution Applied

### 1. Added Migration Script
Created `scripts/migrate_add_status.py` which adds the missing `status` column to the events table.

### 2. Ran Migration
The migration was successfully executed and added the `status` column with default value 'new' for all existing events.

### 3. Added Auto-Migration Logic
Updated `src/storage/sqlite_store.py` to include automatic schema migration:
- `_migrate_schema()` method checks for missing columns
- Automatically adds `status` column if it doesn't exist
- Runs during `initialize_database()` on app startup

### 4. Updated App Initialization
Modified `app.py` to always run `initialize_database()` which includes migration logic.

## Result
✅ The `status` column has been added to your events table
✅ All existing events now have `status = 'new'`
✅ The Database page should now load without errors

## Next Steps

1. **Refresh your browser** (Ctrl+R or Cmd+R) or clear Streamlit cache
2. Navigate to the Database page (🗄️ Database in navigation)
3. The page should now display properly with:
   - Database Status tab showing statistics
   - Clients tab with all your clients
   - Events tab with color-coded event cards
   - Cache tab with cache management

## Event Status Workflow

Events now support a complete status workflow:

```
new → reviewed → actioned → archived
 ↓        ↓         ↓          ↓
Just     You've    You've     Done/
found    seen it   acted      closed
```

You can update event status through the Events tab in the Database page using the buttons:
- **Mark Reviewed** - You've seen the event
- **Mark Actioned** - You've taken action
- **Archive** - Event is complete/no longer relevant

## If You Still See Errors

If you still encounter the "no such column: status" error after refreshing:

1. **Clear Streamlit cache:**
   - In the browser, go to Settings (☰ menu) → "Clear cache"
   - Or add `?clear_cache=true` to the URL

2. **Restart Streamlit:**
   ```bash
   # Stop current process (Ctrl+C)
   # Then restart:
   python -m streamlit run app.py
   ```

3. **Verify migration:**
   ```bash
   python scripts/migrate_add_status.py
   ```
   Should show: "Status column already exists. No migration needed."

## Technical Details

### Migration Script Location
`scripts/migrate_add_status.py`

### SQL Applied
```sql
ALTER TABLE events
ADD COLUMN status TEXT NOT NULL DEFAULT 'new'
```

### Files Modified
- `src/storage/sqlite_store.py` - Added `_migrate_schema()` method
- `app.py` - Updated `init_new_database()` to always run initialization
- `scripts/migrate_add_status.py` - New migration script

## Prevention of Future Issues

The auto-migration logic in `SQLiteStorage` will:
- Check for schema differences on startup
- Automatically add missing columns
- Log migration actions
- Ensure backward compatibility

This means if we add more columns in the future, they'll be automatically migrated without manual intervention.

## Summary

The database schema mismatch has been resolved. The `status` column is now present in your events table, and the Database page should work correctly. Refresh your browser and enjoy your new database management interface!
