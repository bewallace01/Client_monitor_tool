"""
Debug Utilities

Provides debugging tools, logging, and diagnostic capabilities.
"""

import streamlit as st
import os
import json
import sqlite3
import psutil
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import zipfile
import io


class DebugLogger:
    """Centralized debug logging system."""

    @staticmethod
    def log(message: str, level: str = "INFO", details: Optional[Dict] = None):
        """Log a debug message."""
        if not st.session_state.get('debug_mode', False):
            return

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

        log_entry = {
            'timestamp': timestamp,
            'level': level,
            'message': message,
            'details': details or {}
        }

        # Initialize debug logs if not exists
        if 'debug_logs' not in st.session_state:
            st.session_state['debug_logs'] = []

        # Add to logs (keep last 1000 entries)
        st.session_state['debug_logs'].append(log_entry)
        if len(st.session_state['debug_logs']) > 1000:
            st.session_state['debug_logs'] = st.session_state['debug_logs'][-1000:]

    @staticmethod
    def log_api_request(api_name: str, endpoint: str, params: Dict):
        """Log an API request."""
        DebugLogger.log(
            f"API Request: {api_name}",
            level="API",
            details={
                'api': api_name,
                'endpoint': endpoint,
                'params': params
            }
        )

    @staticmethod
    def log_api_response(api_name: str, status_code: int, response_time: float, result_count: int = 0):
        """Log an API response."""
        DebugLogger.log(
            f"API Response: {api_name} ({status_code})",
            level="API",
            details={
                'api': api_name,
                'status_code': status_code,
                'response_time_ms': round(response_time * 1000, 2),
                'result_count': result_count
            }
        )

    @staticmethod
    def log_database_query(query: str, params: tuple = None, execution_time: float = 0):
        """Log a database query."""
        DebugLogger.log(
            "Database Query",
            level="DB",
            details={
                'query': query[:200] + '...' if len(query) > 200 else query,
                'params': str(params) if params else None,
                'execution_time_ms': round(execution_time * 1000, 2)
            }
        )

    @staticmethod
    def log_error(message: str, exception: Exception = None):
        """Log an error."""
        details = {'message': message}
        if exception:
            details['exception_type'] = type(exception).__name__
            details['exception_message'] = str(exception)

        DebugLogger.log(
            message,
            level="ERROR",
            details=details
        )

    @staticmethod
    def get_logs(level: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get debug logs."""
        logs = st.session_state.get('debug_logs', [])

        if level:
            logs = [log for log in logs if log['level'] == level]

        return logs[-limit:]

    @staticmethod
    def clear_logs():
        """Clear all debug logs."""
        st.session_state['debug_logs'] = []


class DebugMetrics:
    """Collects and reports performance metrics."""

    @staticmethod
    def get_system_metrics() -> Dict[str, Any]:
        """Get current system metrics."""
        try:
            process = psutil.Process(os.getpid())

            return {
                'cpu_percent': psutil.cpu_percent(interval=0.1),
                'memory_mb': round(process.memory_info().rss / 1024 / 1024, 2),
                'memory_percent': round(process.memory_percent(), 2),
                'threads': process.num_threads(),
                'disk_usage_percent': psutil.disk_usage('.').percent
            }
        except Exception as e:
            return {'error': str(e)}

    @staticmethod
    def get_database_stats(db_path: str) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            if not os.path.exists(db_path):
                return {'error': 'Database not found'}

            stats = {
                'file_size_mb': round(os.path.getsize(db_path) / 1024 / 1024, 2),
                'modified': datetime.fromtimestamp(os.path.getmtime(db_path)).strftime('%Y-%m-%d %H:%M:%S')
            }

            # Get table stats
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Table counts
            cursor.execute("SELECT COUNT(*) FROM clients")
            stats['clients_count'] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM events")
            stats['events_count'] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM search_cache")
            stats['cache_entries'] = cursor.fetchone()[0]

            # Database size by table
            cursor.execute("""
                SELECT name, SUM(pgsize) / 1024.0 / 1024.0 as size_mb
                FROM dbstat
                GROUP BY name
                ORDER BY size_mb DESC
            """)
            stats['tables'] = {}
            for row in cursor.fetchall():
                stats['tables'][row[0]] = round(row[1], 2)

            conn.close()

            return stats

        except Exception as e:
            return {'error': str(e)}

    @staticmethod
    def get_api_stats() -> Dict[str, Any]:
        """Get API usage statistics."""
        logs = st.session_state.get('debug_logs', [])
        api_logs = [log for log in logs if log['level'] == 'API']

        if not api_logs:
            return {'total_requests': 0}

        api_names = {}
        total_time = 0
        error_count = 0

        for log in api_logs:
            if 'details' in log:
                api_name = log['details'].get('api', 'Unknown')

                if api_name not in api_names:
                    api_names[api_name] = {
                        'count': 0,
                        'total_time': 0,
                        'errors': 0
                    }

                api_names[api_name]['count'] += 1

                if 'response_time_ms' in log['details']:
                    response_time = log['details']['response_time_ms']
                    api_names[api_name]['total_time'] += response_time
                    total_time += response_time

                if 'status_code' in log['details']:
                    if log['details']['status_code'] >= 400:
                        api_names[api_name]['errors'] += 1
                        error_count += 1

        # Calculate averages
        for api in api_names.values():
            if api['count'] > 0:
                api['avg_time'] = round(api['total_time'] / api['count'], 2)

        return {
            'total_requests': len(api_logs),
            'apis': api_names,
            'avg_response_time': round(total_time / len(api_logs), 2) if api_logs else 0,
            'error_count': error_count
        }


class DebugReport:
    """Generates comprehensive debug reports."""

    @staticmethod
    def generate_report() -> Dict[str, Any]:
        """Generate a complete debug report."""
        db_path = st.session_state.settings.get('database_path', 'data/client_intelligence.db')

        report = {
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'version': '1.0.0',
            'system': {
                'os': os.name,
                'python_version': os.sys.version,
                'streamlit_version': st.__version__
            },
            'metrics': DebugMetrics.get_system_metrics(),
            'database': DebugMetrics.get_database_stats(db_path),
            'api_stats': DebugMetrics.get_api_stats(),
            'settings': {
                'demo_mode': st.session_state.settings.get('demo_mode', False),
                'use_mock_apis': st.session_state.settings.get('use_mock_apis', True),
                'database_path': db_path
            },
            'logs': {
                'total_count': len(st.session_state.get('debug_logs', [])),
                'by_level': DebugReport._count_logs_by_level()
            }
        }

        return report

    @staticmethod
    def _count_logs_by_level() -> Dict[str, int]:
        """Count logs by level."""
        logs = st.session_state.get('debug_logs', [])
        counts = {}

        for log in logs:
            level = log.get('level', 'UNKNOWN')
            counts[level] = counts.get(level, 0) + 1

        return counts

    @staticmethod
    def export_debug_package() -> bytes:
        """Export a complete debug package as ZIP."""
        buffer = io.BytesIO()

        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add debug report
            report = DebugReport.generate_report()
            zipf.writestr('debug_report.json', json.dumps(report, indent=2))

            # Add full logs
            logs = st.session_state.get('debug_logs', [])
            zipf.writestr('logs.json', json.dumps(logs, indent=2))

            # Add settings
            settings = st.session_state.get('settings', {})
            # Remove sensitive data
            safe_settings = {k: v for k, v in settings.items()
                           if 'key' not in k.lower() and 'password' not in k.lower()}
            zipf.writestr('settings.json', json.dumps(safe_settings, indent=2))

            # Add database stats
            db_path = st.session_state.settings.get('database_path', 'data/client_intelligence.db')
            db_stats = DebugMetrics.get_database_stats(db_path)
            zipf.writestr('database_stats.json', json.dumps(db_stats, indent=2))

            # Add system info
            system_info = {
                'metrics': DebugMetrics.get_system_metrics(),
                'environment': dict(os.environ) if st.session_state.get('debug_mode') else {}
            }
            zipf.writestr('system_info.json', json.dumps(system_info, indent=2))

            # Add README
            readme = """# Debug Package

This package contains diagnostic information for Client Intelligence Monitor.

## Contents

- `debug_report.json` - Comprehensive debug report with metrics and stats
- `logs.json` - Complete debug logs from this session
- `settings.json` - Application settings (sensitive data removed)
- `database_stats.json` - Database statistics and table information
- `system_info.json` - System metrics and environment info

## Privacy

Sensitive information (API keys, passwords) has been removed from this package.
However, please review all files before sharing.

## Usage

Share this package with support or development team for troubleshooting.

Generated: {}
""".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

            zipf.writestr('README.txt', readme)

        buffer.seek(0)
        return buffer.getvalue()


def render_debug_panel():
    """Render the debug panel in the UI."""
    if not st.session_state.get('debug_mode', False):
        return

    with st.expander("🐛 Debug Panel", expanded=False):
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Metrics", "📝 Logs", "🔧 Tools", "📋 Report"])

        with tab1:
            st.markdown("### System Metrics")

            metrics = DebugMetrics.get_system_metrics()

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("CPU Usage", f"{metrics.get('cpu_percent', 0)}%")
            with col2:
                st.metric("Memory", f"{metrics.get('memory_mb', 0)} MB")
            with col3:
                st.metric("Threads", metrics.get('threads', 0))
            with col4:
                st.metric("Disk Usage", f"{metrics.get('disk_usage_percent', 0)}%")

            st.markdown("---")
            st.markdown("### API Statistics")

            api_stats = DebugMetrics.get_api_stats()

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Requests", api_stats.get('total_requests', 0))
            with col2:
                st.metric("Avg Response Time", f"{api_stats.get('avg_response_time', 0)} ms")
            with col3:
                st.metric("Errors", api_stats.get('error_count', 0))

            if api_stats.get('apis'):
                st.markdown("#### By API")
                for api_name, stats in api_stats['apis'].items():
                    with st.container():
                        st.markdown(f"**{api_name}**")
                        subcol1, subcol2, subcol3 = st.columns(3)
                        with subcol1:
                            st.caption(f"Requests: {stats['count']}")
                        with subcol2:
                            st.caption(f"Avg Time: {stats.get('avg_time', 0)} ms")
                        with subcol3:
                            st.caption(f"Errors: {stats['errors']}")

            st.markdown("---")
            st.markdown("### Database Statistics")

            db_path = st.session_state.settings.get('database_path', 'data/client_intelligence.db')
            db_stats = DebugMetrics.get_database_stats(db_path)

            if 'error' not in db_stats:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("File Size", f"{db_stats.get('file_size_mb', 0)} MB")
                with col2:
                    st.metric("Clients", db_stats.get('clients_count', 0))
                with col3:
                    st.metric("Events", db_stats.get('events_count', 0))

                if db_stats.get('tables'):
                    st.markdown("#### Table Sizes")
                    for table, size in db_stats['tables'].items():
                        st.caption(f"{table}: {size} MB")

        with tab2:
            st.markdown("### Debug Logs")

            # Log level filter
            level_filter = st.selectbox(
                "Filter by Level",
                ["All", "INFO", "API", "DB", "ERROR"],
                key="debug_log_filter"
            )

            # Get logs
            if level_filter == "All":
                logs = DebugLogger.get_logs(limit=100)
            else:
                logs = DebugLogger.get_logs(level=level_filter, limit=100)

            st.caption(f"Showing last {len(logs)} logs")

            # Display logs
            for log in reversed(logs):
                level = log.get('level', 'INFO')

                # Color code by level
                if level == 'ERROR':
                    color = '#d32f2f'
                elif level == 'API':
                    color = '#1976d2'
                elif level == 'DB':
                    color = '#388e3c'
                else:
                    color = '#666'

                with st.container():
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        st.markdown(f"<span style='color: {color}; font-weight: bold;'>[{level}]</span>", unsafe_allow_html=True)
                        st.caption(log.get('timestamp', ''))
                    with col2:
                        st.markdown(log.get('message', ''))
                        if log.get('details'):
                            with st.expander("Details"):
                                st.json(log['details'])

            # Clear logs button
            if st.button("🗑️ Clear Logs"):
                DebugLogger.clear_logs()
                st.rerun()

        with tab3:
            st.markdown("### Debug Tools")

            st.markdown("#### Test Logging")

            if st.button("Test INFO Log"):
                DebugLogger.log("Test INFO message", level="INFO", details={'test': True})
                st.success("INFO log created")

            if st.button("Test ERROR Log"):
                DebugLogger.log_error("Test error message", Exception("Test exception"))
                st.error("ERROR log created")

            st.markdown("---")

            st.markdown("#### Database Tools")

            if st.button("Run Database Vacuum"):
                try:
                    db_path = st.session_state.settings.get('database_path', 'data/client_intelligence.db')
                    conn = sqlite3.connect(db_path)
                    conn.execute("VACUUM")
                    conn.close()
                    st.success("✅ Database vacuumed successfully")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

            if st.button("Analyze Database"):
                try:
                    db_path = st.session_state.settings.get('database_path', 'data/client_intelligence.db')
                    conn = sqlite3.connect(db_path)
                    conn.execute("ANALYZE")
                    conn.close()
                    st.success("✅ Database analyzed successfully")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

            st.markdown("---")

            st.markdown("#### Cache Tools")

            if st.button("Clear Cache"):
                try:
                    db_path = st.session_state.settings.get('database_path', 'data/client_intelligence.db')
                    conn = sqlite3.connect(db_path)
                    conn.execute("DELETE FROM search_cache")
                    conn.commit()
                    conn.close()
                    st.success("✅ Cache cleared successfully")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

        with tab4:
            st.markdown("### Debug Report")

            st.markdown("Generate a comprehensive debug report for troubleshooting.")

            if st.button("📊 Generate Report", use_container_width=True):
                report = DebugReport.generate_report()
                st.json(report)

            st.markdown("---")

            st.markdown("### Export Debug Package")

            st.markdown("""
            Export a complete debug package including:
            - Debug report with metrics
            - Complete logs
            - Settings (sensitive data removed)
            - Database statistics
            - System information
            """)

            if st.button("📦 Export Debug Package", use_container_width=True, type="primary"):
                try:
                    debug_package = DebugReport.export_debug_package()

                    st.download_button(
                        label="⬇️ Download Debug Package",
                        data=debug_package,
                        file_name=f"debug_package_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                        mime="application/zip",
                        use_container_width=True
                    )

                    st.success("✅ Debug package created successfully!")

                except Exception as e:
                    st.error(f"❌ Error creating debug package: {e}")


def initialize_debug_mode():
    """Initialize debug mode from settings."""
    if 'debug_mode' not in st.session_state:
        # Check if settings exist, otherwise default to False
        if hasattr(st.session_state, 'settings') and st.session_state.settings:
            st.session_state['debug_mode'] = st.session_state.settings.get('debug_mode', False)
        else:
            st.session_state['debug_mode'] = False

    if 'debug_logs' not in st.session_state:
        st.session_state['debug_logs'] = []
