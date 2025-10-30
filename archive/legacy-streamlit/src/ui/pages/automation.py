"""Automation and scheduler control panel."""

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from typing import List

from src.storage import SQLiteStorage
from src.scheduler.jobs import run_job, JOBS
from src.models.job_run import JobRun


def render_status_indicator(status: str):
    """Render status indicator with icon and color."""
    status_config = {
        "running": {"icon": "🟢", "label": "Running", "color": "#10b981"},
        "idle": {"icon": "🟡", "label": "Idle", "color": "#f59e0b"},
        "stopped": {"icon": "🔴", "label": "Stopped", "color": "#ef4444"},
    }

    config = status_config.get(status, status_config["idle"])

    st.markdown(f"""
    <div style="text-align: center; padding: 1rem; background-color: {config['color']}20;
                border-radius: 8px; border: 2px solid {config['color']};">
        <div style="font-size: 2rem;">{config['icon']}</div>
        <div style="font-weight: 600; color: {config['color']}; margin-top: 0.5rem;">
            {config['label']}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_job_run_row(job_run: JobRun, storage: SQLiteStorage):
    """Render a single job run row."""
    # Status icon
    status_icons = {
        "completed": "✅",
        "failed": "❌",
        "running": "⏳",
        "cancelled": "🚫",
    }
    status_icon = status_icons.get(job_run.status, "❓")

    # Duration
    if job_run.duration_seconds():
        duration = f"{job_run.duration_seconds():.1f}s"
    else:
        duration = "—"

    # Format job name
    job_display_names = {
        "daily_scan": "Daily Scan",
        "weekly_report": "Weekly Report",
        "cache_cleanup": "Cache Cleanup",
    }
    job_display = job_display_names.get(job_run.job_name, job_run.job_name)

    with st.container(border=True):
        col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 1, 1, 3, 1])

        with col1:
            st.write(f"**{job_display}**")

        with col2:
            st.write(job_run.start_time.strftime("%Y-%m-%d %H:%M"))

        with col3:
            st.write(duration)

        with col4:
            st.write(f"{status_icon} {job_run.status.capitalize()}")

        with col5:
            if job_run.results_summary:
                summary = job_run.results_summary[:60] + "..." if len(job_run.results_summary) > 60 else job_run.results_summary
                st.caption(summary)
            elif job_run.error_message:
                st.caption(f"⚠️ {job_run.error_message[:60]}")

        with col6:
            if st.button("Details", key=f"details_{job_run.id}", use_container_width=True):
                st.session_state.viewing_job_run = job_run.id
                st.rerun()


def render_job_detail_modal(job_run: JobRun):
    """Render detailed job run information."""
    if st.button("✕ Close", key="close_job_detail"):
        del st.session_state.viewing_job_run
        st.rerun()

    st.markdown("---")

    # Header
    st.markdown(f"## Job Run Details: {job_run.job_name}")

    # Status and timing
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Status", job_run.status.capitalize())

    with col2:
        if job_run.duration_seconds():
            st.metric("Duration", f"{job_run.duration_seconds():.1f}s")
        else:
            st.metric("Duration", "In progress...")

    with col3:
        st.metric("Start Time", job_run.start_time.strftime("%H:%M:%S"))

    st.divider()

    # Results or error
    if job_run.status == "completed" and job_run.results_summary:
        st.subheader("✅ Results")
        st.success(job_run.results_summary)
    elif job_run.status == "failed" and job_run.error_message:
        st.subheader("❌ Error")
        st.error(job_run.error_message)

    # Metadata
    if job_run.metadata:
        st.subheader("📊 Metadata")
        for key, value in job_run.metadata.items():
            st.write(f"**{key}:** {value}")


def render_manual_scan_interface(storage: SQLiteStorage):
    """Render manual scan controls."""
    st.subheader("🚀 Manual Scan")

    # Get all clients
    all_clients = storage.get_all_clients()
    active_clients = [c for c in all_clients if c.is_active]
    high_priority = [c for c in active_clients if c.priority == "high"]

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔍 Run Full Scan", type="primary", use_container_width=True):
            st.session_state.running_scan = "full"
            st.rerun()
        st.caption(f"Scan all {len(active_clients)} active clients")

    with col2:
        if st.button("⚡ Quick Scan", use_container_width=True):
            st.session_state.running_scan = "quick"
            st.rerun()
        st.caption(f"Scan {len(high_priority)} high-priority clients")

    st.divider()

    # Targeted scan
    st.markdown("**🎯 Targeted Scan**")
    selected_clients = st.multiselect(
        "Select specific clients",
        options=[c.name for c in active_clients],
        key="targeted_scan_clients"
    )

    if selected_clients:
        if st.button(f"Scan {len(selected_clients)} Selected Client(s)", use_container_width=True):
            st.session_state.running_scan = "targeted"
            st.session_state.scan_targets = selected_clients
            st.rerun()

    # Execute scans
    if st.session_state.get("running_scan"):
        scan_type = st.session_state.running_scan

        st.divider()
        st.subheader(f"Running {scan_type.capitalize()} Scan...")

        # Check if scan has already completed
        if not st.session_state.get("scan_completed"):
            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                # Determine which clients to scan
                client_filter = None
                job_name_suffix = "scan"

                if scan_type == "full":
                    # Scan all active clients
                    client_filter = None
                    job_name_suffix = "full_scan"
                elif scan_type == "quick":
                    # Scan only high priority clients
                    client_filter = [c.name for c in high_priority]
                    job_name_suffix = "quick_scan"
                elif scan_type == "targeted":
                    # Scan only selected clients
                    client_filter = st.session_state.get("scan_targets", [])
                    job_name_suffix = "targeted_scan"

                # Run the scan job with appropriate filters
                with st.spinner("Scanning..."):
                    from src.scheduler.jobs import daily_scan_job
                    job_run = daily_scan_job(storage, client_filter=client_filter, job_name=job_name_suffix)

                progress_bar.progress(1.0)

                # Store results in session state
                st.session_state.scan_completed = True
                st.session_state.scan_result = job_run

                st.rerun()

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.session_state.scan_completed = True
                st.session_state.scan_error = str(e)
                st.rerun()

        else:
            # Display results
            if st.session_state.get("scan_result"):
                job_run = st.session_state.scan_result

                if job_run.status == "completed":
                    st.success(f"✅ Scan completed: {job_run.results_summary}")
                    st.json(job_run.metadata)
                else:
                    st.error(f"❌ Scan failed: {job_run.error_message}")
            elif st.session_state.get("scan_error"):
                st.error(f"❌ Error: {st.session_state.scan_error}")

            # Action buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Done", use_container_width=True):
                    # Clear all scan-related session state
                    del st.session_state.running_scan
                    del st.session_state.scan_completed
                    if "scan_targets" in st.session_state:
                        del st.session_state.scan_targets
                    if "scan_result" in st.session_state:
                        del st.session_state.scan_result
                    if "scan_error" in st.session_state:
                        del st.session_state.scan_error
                    st.rerun()

            with col2:
                if st.button("🔄 Run Again", use_container_width=True):
                    # Keep running_scan and scan_targets, but clear completion flags
                    del st.session_state.scan_completed
                    if "scan_result" in st.session_state:
                        del st.session_state.scan_result
                    if "scan_error" in st.session_state:
                        del st.session_state.scan_error
                    st.rerun()


def render_automation_page():
    """Main automation control panel."""
    st.markdown('<h1 class="main-header">Automation & Monitoring</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Configure and monitor automated scanning</p>', unsafe_allow_html=True)

    # Initialize storage
    storage = SQLiteStorage()
    storage.connect()

    # Check if viewing job detail
    if st.session_state.get("viewing_job_run"):
        job_run = storage.get_job_run(st.session_state.viewing_job_run)
        if job_run:
            render_job_detail_modal(job_run)
            return
        else:
            del st.session_state.viewing_job_run

    # Real-time Scheduler Status Widget (moved from sidebar)
    from src.scheduler.control import is_scheduler_running, start_scheduler, stop_scheduler
    from src.scheduler.runner import get_scheduler_status

    st.subheader("🤖 Real-time Scheduler Status")

    col1, col2, col3 = st.columns([1, 2, 2])

    with col1:
        # Get scheduler status
        is_running = is_scheduler_running()
        status_data = get_scheduler_status()

        # Status indicator
        if is_running:
            st.markdown("🟢 **Active**")
        else:
            st.markdown("🔴 **Stopped**")

    with col2:
        # Next run countdown
        if status_data.get("next_run"):
            try:
                next_run = datetime.fromisoformat(status_data["next_run"])
                time_until = next_run - datetime.now()
                hours = int(time_until.total_seconds() // 3600)
                minutes = int((time_until.total_seconds() % 3600) // 60)
                st.metric("Next Scan", f"{hours}h {minutes}m")
            except Exception:
                st.metric("Next Scan", "Not scheduled")
        else:
            st.metric("Next Scan", "Not scheduled")

    with col3:
        # Start/Stop button
        if is_running:
            if st.button("⏸️ Stop Scheduler", use_container_width=True):
                if stop_scheduler():
                    st.success("Scheduler stopped")
                    st.rerun()
                else:
                    st.error("Failed to stop scheduler")
        else:
            if st.button("▶️ Start Scheduler", use_container_width=True, type="primary"):
                if start_scheduler():
                    st.success("Scheduler started")
                    st.rerun()
                else:
                    st.error("Failed to start scheduler")

    # Recent job status
    if status_data.get("last_runs"):
        with st.expander("📋 Recent Jobs Summary"):
            cols = st.columns(3)
            for idx, (job_name, job_info) in enumerate(list(status_data["last_runs"].items())[:3]):
                with cols[idx]:
                    status_icon = "✅" if job_info["status"] == "completed" else "❌"
                    st.markdown(f"{status_icon} **{job_name}**")
                    summary = job_info.get("summary") or "No summary"
                    summary_display = summary[:40] if summary else "No summary"
                    st.caption(summary_display + "...")

    st.divider()

    # Scheduler Control Panel
    st.subheader("🎛️ Scheduler Control")

    col1, col2, col3 = st.columns([2, 2, 2])

    with col1:
        monitoring_active = st.toggle(
            "Monitoring Active",
            value=st.session_state.get("monitoring_active", False),
            key="monitoring_toggle"
        )
        if monitoring_active != st.session_state.get("monitoring_active", False):
            st.session_state.monitoring_active = monitoring_active
            if monitoring_active:
                st.success("✅ Monitoring activated!")
            else:
                st.warning("⚠️ Monitoring paused")

    with col2:
        status = "running" if st.session_state.get("monitoring_active", False) else "stopped"
        render_status_indicator(status)

    with col3:
        # Next scheduled run
        st.markdown("**Next Scheduled Run**")
        # Calculate next run (example: tomorrow at 8 AM)
        next_run = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
        if next_run < datetime.now():
            next_run += timedelta(days=1)

        time_until = next_run - datetime.now()
        hours = int(time_until.total_seconds() // 3600)
        minutes = int((time_until.total_seconds() % 3600) // 60)

        st.metric("Daily Scan", f"in {hours}h {minutes}m")

    st.divider()

    # Job Schedule Configuration
    st.subheader("⏰ Schedule Configuration")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Daily Scan**")
        daily_time = st.time_input(
            "Time",
            value=datetime.strptime("08:00", "%H:%M").time(),
            key="daily_scan_time",
            label_visibility="collapsed"
        )
        if st.button("Run Now", key="run_daily", use_container_width=True):
            with st.spinner("Running daily scan..."):
                job_run = run_job("daily_scan", storage)
                if job_run.status == "completed":
                    st.success(f"✅ {job_run.results_summary}")
                else:
                    st.error(f"❌ {job_run.error_message}")
                st.rerun()

    with col2:
        st.markdown("**Weekly Report**")
        report_day = st.selectbox(
            "Day",
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            index=0,
            key="report_day",
            label_visibility="collapsed"
        )
        report_time = st.time_input(
            "Time",
            value=datetime.strptime("09:00", "%H:%M").time(),
            key="report_time",
            label_visibility="collapsed"
        )
        if st.button("Run Now", key="run_weekly", use_container_width=True):
            with st.spinner("Generating weekly report..."):
                job_run = run_job("weekly_report", storage)
                if job_run.status == "completed":
                    st.success("✅ Report generated")
                    with st.expander("View Report"):
                        st.text(job_run.results_summary)
                else:
                    st.error(f"❌ {job_run.error_message}")
                st.rerun()

    with col3:
        st.markdown("**Cache Cleanup**")
        cleanup_time = st.time_input(
            "Time",
            value=datetime.strptime("02:00", "%H:%M").time(),
            key="cleanup_time",
            label_visibility="collapsed"
        )
        if st.button("Run Now", key="run_cleanup", use_container_width=True):
            with st.spinner("Cleaning cache..."):
                job_run = run_job("cache_cleanup", storage)
                if job_run.status == "completed":
                    st.success(f"✅ {job_run.results_summary}")
                else:
                    st.error(f"❌ {job_run.error_message}")
                st.rerun()

    if st.button("💾 Save Schedule", type="primary", use_container_width=True):
        # Save schedule to session state or database
        st.session_state.schedule_config = {
            "daily_scan_time": daily_time.strftime("%H:%M"),
            "report_day": report_day,
            "report_time": report_time.strftime("%H:%M"),
            "cleanup_time": cleanup_time.strftime("%H:%M"),
        }
        st.success("✅ Schedule saved!")

    st.divider()

    # Manual Scan Interface
    render_manual_scan_interface(storage)

    st.divider()

    # Job History
    st.subheader("📜 Job History")

    # Filters
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        filter_job_type = st.multiselect(
            "Job Type",
            options=["All"] + list(JOBS.keys()),
            default=["All"],
            key="filter_job_type"
        )

    with col2:
        filter_status = st.multiselect(
            "Status",
            options=["All", "completed", "failed", "running", "cancelled"],
            default=["All"],
            key="filter_status"
        )

    with col3:
        limit = st.number_input("Show last", min_value=10, max_value=100, value=20, step=10)

    # Get job runs
    all_runs = storage.get_recent_job_runs(limit=limit)

    # Apply filters
    if "All" not in filter_job_type:
        all_runs = [r for r in all_runs if r.job_name in filter_job_type]

    if "All" not in filter_status:
        all_runs = [r for r in all_runs if r.status in filter_status]

    # Display job runs
    if all_runs:
        st.caption(f"Showing {len(all_runs)} job run(s)")

        for job_run in all_runs:
            render_job_run_row(job_run, storage)
    else:
        st.info("📭 No job runs found. Run a job to see history here.")

    st.divider()

    # Settings
    st.subheader("⚙️ Settings")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Job Enablement**")
        enable_daily = st.checkbox("Enable Daily Scan", value=True, key="enable_daily")
        enable_weekly = st.checkbox("Enable Weekly Report", value=True, key="enable_weekly")
        enable_cleanup = st.checkbox("Enable Cache Cleanup", value=True, key="enable_cleanup")

    with col2:
        st.markdown("**Scan Frequency**")
        frequency = st.select_slider(
            "Frequency",
            options=["Once daily", "Twice daily", "Every 6 hours", "Every 4 hours"],
            value="Once daily",
            key="scan_frequency",
            label_visibility="collapsed"
        )

    st.markdown("**Quiet Hours**")
    col1, col2 = st.columns(2)
    with col1:
        quiet_start = st.time_input("Start", value=datetime.strptime("22:00", "%H:%M").time())
    with col2:
        quiet_end = st.time_input("End", value=datetime.strptime("06:00", "%H:%M").time())

    st.caption("Scans will not run during quiet hours")

    st.markdown("**Notifications**")
    col1, col2, col3 = st.columns(3)
    with col1:
        notify_success = st.checkbox("Notify on success", value=False)
    with col2:
        notify_errors = st.checkbox("Notify on errors", value=True)
    with col3:
        notify_weekly = st.checkbox("Weekly summary email", value=True)

    if st.button("💾 Save Settings", use_container_width=True, type="primary"):
        st.session_state.automation_settings = {
            "enable_daily": enable_daily,
            "enable_weekly": enable_weekly,
            "enable_cleanup": enable_cleanup,
            "scan_frequency": frequency,
            "quiet_start": quiet_start.strftime("%H:%M"),
            "quiet_end": quiet_end.strftime("%H:%M"),
            "notify_success": notify_success,
            "notify_errors": notify_errors,
            "notify_weekly": notify_weekly,
        }
        st.success("✅ Settings saved!")

    # Statistics
    st.divider()
    st.subheader("📊 Statistics")

    stats = storage.get_job_stats()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Runs", stats["total"])

    with col2:
        completed = stats["by_status"].get("completed", 0)
        st.metric("Completed", completed)

    with col3:
        failed = stats["by_status"].get("failed", 0)
        st.metric("Failed", failed)

    with col4:
        st.metric("Recent Failures (7d)", stats["recent_failures"])

    # Success rate
    if stats["total"] > 0:
        success_rate = (completed / stats["total"]) * 100
        st.progress(success_rate / 100)
        st.caption(f"Success Rate: {success_rate:.1f}%")
