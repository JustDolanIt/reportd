CREATE SCHEMA reportd
  AUTHORIZATION own_mon;

GRANT ALL ON SCHEMA reportd TO own_mon;
GRANT USAGE ON SCHEMA reportd TO dev_mon;
GRANT USAGE ON SCHEMA reportd TO srv_mon;

CREATE TYPE reportd.status AS ENUM
   ('open',
    'closed',
    'assign',
    'ack',
    'expired',
    'unknown');
ALTER TYPE reportd.status
  OWNER TO own_mon;

CREATE TYPE reportd.severity AS ENUM
   ('security',
    'critical',
    'major',
    'minor',
    'warning',
    'indeterminate',
    'cleared',
    'normal',
    'ok',
    'informational',
    'debug',
    'trace',
    'unknown');
ALTER TYPE reportd.severity
  OWNER TO own_mon;

CREATE TABLE reportd.reports
(
  id serial NOT NULL,
  services text[],
  exclude_services text[],
  resource text[],
  exclude_resource text[],
  tags text[],
  exclude_tags text[],
  events text[],
  exclude_events text[],
  severity text[],
  status reportd.status DEFAULT 'open'::reportd.status,
  scenarios text[] NOT NULL,
  kwargs jsonb,
  name_prefix text NOT NULL,
  description text,
  CONSTRAINT reports_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE reportd.reports
  OWNER TO own_mon;
GRANT ALL ON TABLE reportd.reports TO own_mon;
GRANT ALL ON TABLE reportd.reports TO dev_mon;
GRANT ALL ON TABLE reportd.reports TO srv_mon;
