import { useEffect, useState } from 'react';
import { Activity, ArrowRight, Bell, Building2, CalendarCheck, CalendarDays, ChartNoAxesColumn, CircleUserRound, ClipboardCheck, Users } from 'lucide-react';
import { Link } from 'react-router-dom';
import { adminKpis } from '../../data/adminMock';
import { getBookingAnalytics, listAdminUsers, listAuditEvents } from '../../api/admin';
import { listAdminEvents } from '../../api/events';
import type { ApiAdminUser, ApiAuditEvent, ApiBookingAnalytics, ApiCampusEvent } from '../../api/types';
import { AdminMetric, AdminPageHeader, AdminPanel } from './shared';

const metricIcons = [Users, CalendarDays, CalendarCheck, Activity];
const pieColors = ['#5146f6', '#3d88e8', '#27b39a', '#8b69dc', '#e879f9', '#fb923c'];

function activityIconFor(action: string) {
  const lower = action.toLowerCase();
  if (lower.includes('registration') || lower.includes('register')) return ClipboardCheck;
  if (lower.includes('booking') || lower.includes('venue')) return CalendarCheck;
  if (lower.includes('user') || lower.includes('account')) return CircleUserRound;
  if (lower.includes('provider') || lower.includes('approve')) return Building2;
  return Activity;
}

function polarToCartesian(centerX: number, centerY: number, radius: number, angleInDegrees: number) {
  const angleInRadians = ((angleInDegrees - 90) * Math.PI) / 180.0;
  return { x: centerX + radius * Math.cos(angleInRadians), y: centerY + radius * Math.sin(angleInRadians) };
}

function describeArc(x: number, y: number, radius: number, startAngle: number, endAngle: number) {
  const start = polarToCartesian(x, y, radius, endAngle);
  const end = polarToCartesian(x, y, radius, startAngle);
  const largeArcFlag = endAngle - startAngle <= 180 ? '0' : '1';
  const d = [
    'M', start.x, start.y,
    'A', radius, radius, 0, largeArcFlag, 0, end.x, end.y,
    'L', x, y,
  ].join(' ');
  return d;
}

function VenueDonutChart({ venues }: { venues: { name: string; value: number; color: string }[] }) {
  const total = venues.reduce((sum, v) => sum + v.value, 0);
  const cx = 56;
  const cy = 56;
  const radius = 44;
  const innerRadius = 28;
  let slices: { d: string; color: string; name: string; value: number; percent: number }[] = [];
  let startAngle = 0;
  venues.forEach((venue, index) => {
    const sliceAngle = total > 0 ? (venue.value / total) * 360 : 0;
    const endAngle = startAngle + sliceAngle;
    slices.push({
      d: describeArc(cx, cy, radius, startAngle, endAngle),
      color: pieColors[index % pieColors.length],
      name: venue.name,
      value: venue.value,
      percent: total > 0 ? Math.round((venue.value / total) * 100) : 0,
    });
    startAngle = endAngle;
  });
  return (
    <figure className="admin-popular-venues" aria-label="Booking counts by venue from live admin analytics">
      <svg viewBox="0 0 112 112" className="admin-pie" role="img" aria-labelledby="admin-pie-title">
        <title id="admin-pie-title">Bookings by venue</title>
        {slices.map((slice, index) => <path key={index} d={slice.d} fill={slice.color} />)}
        <circle cx={cx} cy={cy} r={innerRadius} fill="#fff" />
      </svg>
      <div className="admin-pie-center"><span>Bookings<small>by venue</small></span></div>
      <ul className="admin-pie-legend">{slices.map((slice) => <li key={slice.name}><i style={{ background: slice.color }} /><span>{slice.name}</span><strong>{slice.value}</strong><small>{slice.percent}%</small></li>)}</ul>
    </figure>
  );
}

export function AdminDashboardPage() {
  const [period, setPeriod] = useState('Last 30 Days');
  const [analytics, setAnalytics] = useState<ApiBookingAnalytics | null>(null);
  const [users, setUsers] = useState<ApiAdminUser[]>([]);
  const [events, setEvents] = useState<ApiCampusEvent[]>([]);
  const [audit, setAudit] = useState<ApiAuditEvent[]>([]);
  const [error, setError] = useState('');

  useEffect(() => {
    Promise.all([
      getBookingAnalytics().then(setAnalytics).catch((err) => setError(err instanceof Error ? err.message : 'Analytics could not be loaded.')),
      listAdminUsers({ limit: 100 }).then(setUsers).catch(() => undefined),
      listAdminEvents(true).then(setEvents).catch(() => undefined),
      listAuditEvents({ limit: 50 }).then(setAudit).catch(() => undefined),
    ]).catch(() => undefined);
  }, []);

  const totalUsers = users.length;
  const totalEvents = events.length;
  const dashboardKpis = [
    { label: 'Total Users', value: String(totalUsers), trend: 'Live', tone: 'violet' },
    { label: 'Total Events', value: String(totalEvents), trend: 'Live', tone: 'blue' },
    { label: 'Total Bookings', value: analytics ? String(analytics.total_bookings) : adminKpis[2].value, trend: analytics ? 'Live' : '-', tone: 'mint' },
    { label: 'Expected Attendance', value: analytics ? String(analytics.total_expected_attendance) : adminKpis[3].value, trend: analytics ? 'Live' : '-', tone: 'amber' },
  ];

  const popularVenues = analytics?.venue_usage.slice(0, 5).map((venue, index) => ({ name: venue.venue_name, value: venue.booking_count, color: pieColors[index % pieColors.length] }));

  const recentActivity = audit.slice(0, 4).map((event) => ({
    title: event.action.replace(/\b\w/g, (c) => c.toUpperCase()),
    detail: `${event.actor_type}${event.target_type ? ` · ${event.target_type}` : ''} · ${new Date(event.created_at).toLocaleString('en-KE', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}`,
    icon: activityIconFor(event.action),
    outcome: event.outcome,
  }));

  return (
    <section className="admin-dashboard-page">
      <AdminPageHeader title="Dashboard" description="Overview of your UniSpot campus platform." eyebrow="PLATFORM OVERVIEW" action={<label className="admin-period-select"><CalendarDays size={15} aria-hidden="true" /><span className="sr-only">Dashboard period</span><select value={period} onChange={(event) => setPeriod(event.target.value)}><option>Last 30 Days</option><option>Last 90 Days</option><option>This Semester</option></select></label>} />
      {error && <p className="admin-feedback admin-feedback--warning" role="status" aria-live="polite">{error}</p>}
      <div className="admin-kpi-grid" aria-label={`Platform metrics for ${period}`}>
        {dashboardKpis.map((metric, index) => <AdminMetric key={metric.label} {...metric} icon={metricIcons[index]} />)}
      </div>

      <div className="admin-dashboard-grid">
        <AdminPanel title="Event Registrations Trend" className="admin-trend-panel" action={<label className="admin-small-select"><span className="sr-only">Trend chart period</span><select defaultValue="This Month"><option>This Month</option><option>This Semester</option></select></label>}>
          <div className="admin-chart-summary"><span>Registrations <strong>{events.reduce((sum, e) => sum + e.confirmed_registrations, 0)}</strong></span><span className="admin-trend-positive">Live data</span></div>
          <figure className="admin-line-chart"><svg viewBox="0 0 640 220" role="img" aria-labelledby="admin-trend-title admin-trend-desc" preserveAspectRatio="none"><title id="admin-trend-title">Campus event registrations trend</title><desc id="admin-trend-desc">Illustrative trend chart. Per-period registration totals require a dedicated analytics endpoint.</desc><g className="admin-grid-lines"><line x1="42" y1="25" x2="626" y2="25" /><line x1="42" y1="72" x2="626" y2="72" /><line x1="42" y1="119" x2="626" y2="119" /><line x1="42" y1="166" x2="626" y2="166" /></g><g className="admin-y-labels"><text x="4" y="29">200</text><text x="4" y="76">150</text><text x="4" y="123">100</text><text x="10" y="170">50</text><text x="18" y="208">0</text></g><path className="admin-chart-area" d="M42 155 L97 163 L151 142 L205 151 L260 112 L314 126 L369 91 L423 119 L478 77 L532 93 L586 55 L626 30 L626 190 L42 190Z" /><polyline className="admin-chart-line" points="42,155 97,163 151,142 205,151 260,112 314,126 369,91 423,119 478,77 532,93 586,55 626,30" /><g className="admin-chart-dots"><circle cx="42" cy="155" r="3" /><circle cx="151" cy="142" r="3" /><circle cx="260" cy="112" r="3" /><circle cx="369" cy="91" r="3" /><circle cx="478" cy="77" r="3" /><circle cx="586" cy="55" r="3" /><circle cx="626" cy="30" r="3" /></g></svg><figcaption><span>Sep 15</span><span>Sep 18</span><span>Sep 21</span><span>Sep 24</span><span>Sep 27</span><span>Sep 30</span><span>Oct 03</span><span>Oct 06</span><span>Oct 09</span></figcaption></figure>
        </AdminPanel>

        <AdminPanel title="Popular Venues"><VenueDonutChart venues={popularVenues ?? []} /></AdminPanel>

        <AdminPanel title="Recent Activity" action={<Link className="admin-panel-link" to="/admin/audit-logs">View all <ArrowRight size={13} /></Link>}>
          <ul className="admin-activity-list">{recentActivity.map(({ title, detail, icon: Icon, outcome }) => <li key={title + detail}><span className="admin-activity-icon"><Icon size={14} aria-hidden="true" /></span><span><strong>{title}</strong><small>{detail}</small></span><span className={`admin-activity-outcome admin-activity-outcome--${outcome}`}>{outcome}</span></li>)}</ul>
        </AdminPanel>
      </div>

      <div className="admin-dashboard-bottom">
        <section className="admin-announcement"><span className="admin-announcement-icon"><Bell size={21} aria-hidden="true" /></span><div><strong>System Announcement</strong><p>The platform will be under maintenance on 12th October 2026 from 8:00 AM–12:00 PM.</p></div><Link className="button button--primary button--small" to="/admin/maintenance">View details</Link></section>
        <AdminPanel title="Quick Actions" className="admin-quick-panel"><div className="admin-quick-actions"><Link to="/admin/venues?create=1"><span><Building2 size={16} /></span>Add Venue</Link><Link to="/admin/events?create=1"><span><CalendarDays size={16} /></span>Add Event</Link><Link to="/admin/users?create=1"><span><Users size={16} /></span>Add User</Link><Link to="/admin/analytics-reports"><span><ChartNoAxesColumn size={16} /></span>View Reports</Link></div></AdminPanel>
      </div>
      <p className="admin-sample-note">All KPIs, recent activity, and the venue pie chart now load from the Admin API. The registrations trend chart remains illustrative until a per-period trend endpoint is added.</p>
    </section>
  );
}
