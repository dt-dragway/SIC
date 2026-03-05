--
-- PostgreSQL database dump
--

\restrict 5WxBnWnbJnjiBuAZFfd9UIKXrqqKhAY5tcZKtaLPp7bswIya0nf65JGBr3nwR1n

-- Dumped from database version 16.11
-- Dumped by pg_dump version 16.11

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: agent_trades; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.agent_trades (
    id integer NOT NULL,
    trade_id character varying(50) NOT NULL,
    symbol character varying(20) NOT NULL,
    side character varying(10) NOT NULL,
    entry_price double precision NOT NULL,
    exit_price double precision NOT NULL,
    pnl double precision NOT NULL,
    signals_used text,
    patterns_detected text,
    created_at timestamp without time zone
);


ALTER TABLE public.agent_trades OWNER TO postgres;

--
-- Name: TABLE agent_trades; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.agent_trades IS 'Trades del Agente IA para sincronización con agent_memory.json';


--
-- Name: agent_trades_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.agent_trades_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.agent_trades_id_seq OWNER TO postgres;

--
-- Name: agent_trades_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.agent_trades_id_seq OWNED BY public.agent_trades.id;


--
-- Name: alerts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alerts (
    id integer NOT NULL,
    user_id integer NOT NULL,
    type character varying(50) NOT NULL,
    symbol character varying(20),
    condition character varying(20),
    target_value double precision,
    is_active boolean,
    triggered_at timestamp without time zone,
    created_at timestamp without time zone
);


ALTER TABLE public.alerts OWNER TO postgres;

--
-- Name: alerts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.alerts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.alerts_id_seq OWNER TO postgres;

--
-- Name: alerts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.alerts_id_seq OWNED BY public.alerts.id;


--
-- Name: funding_rate_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.funding_rate_history (
    id integer NOT NULL,
    symbol character varying(20) NOT NULL,
    funding_rate double precision NOT NULL,
    mark_price double precision NOT NULL,
    index_price double precision NOT NULL,
    open_interest double precision,
    "timestamp" timestamp without time zone,
    next_funding_time timestamp without time zone
);


ALTER TABLE public.funding_rate_history OWNER TO postgres;

--
-- Name: funding_rate_history_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.funding_rate_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.funding_rate_history_id_seq OWNER TO postgres;

--
-- Name: funding_rate_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.funding_rate_history_id_seq OWNED BY public.funding_rate_history.id;


--
-- Name: journal_entries; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.journal_entries (
    id integer NOT NULL,
    user_id integer NOT NULL,
    symbol character varying(20) NOT NULL,
    side character varying(10),
    entry_price double precision,
    exit_price double precision,
    pnl double precision,
    mood character varying(50),
    strategy character varying(100),
    notes text,
    lessons text,
    rating integer,
    created_at timestamp without time zone
);


ALTER TABLE public.journal_entries OWNER TO postgres;

--
-- Name: journal_entries_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.journal_entries_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.journal_entries_id_seq OWNER TO postgres;

--
-- Name: journal_entries_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.journal_entries_id_seq OWNED BY public.journal_entries.id;


--
-- Name: order_book_snapshots; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.order_book_snapshots (
    id integer NOT NULL,
    symbol character varying(20) NOT NULL,
    best_bid double precision NOT NULL,
    best_ask double precision NOT NULL,
    spread double precision NOT NULL,
    bids_json text,
    asks_json text,
    bid_volume_10 double precision,
    ask_volume_10 double precision,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.order_book_snapshots OWNER TO postgres;

--
-- Name: order_book_snapshots_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.order_book_snapshots_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.order_book_snapshots_id_seq OWNER TO postgres;

--
-- Name: order_book_snapshots_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.order_book_snapshots_id_seq OWNED BY public.order_book_snapshots.id;


--
-- Name: p2p_rates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.p2p_rates (
    id integer NOT NULL,
    avg_buy_price double precision NOT NULL,
    avg_sell_price double precision NOT NULL,
    best_buy_price double precision NOT NULL,
    best_sell_price double precision NOT NULL,
    spread_percent double precision NOT NULL,
    offers_count integer,
    volume double precision,
    recorded_at timestamp without time zone
);


ALTER TABLE public.p2p_rates OWNER TO postgres;

--
-- Name: p2p_rates_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.p2p_rates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.p2p_rates_id_seq OWNER TO postgres;

--
-- Name: p2p_rates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.p2p_rates_id_seq OWNED BY public.p2p_rates.id;


--
-- Name: signals; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.signals (
    id integer NOT NULL,
    symbol character varying(20) NOT NULL,
    type character varying(10) NOT NULL,
    strength character varying(20) NOT NULL,
    confidence double precision NOT NULL,
    entry_price double precision NOT NULL,
    take_profit double precision NOT NULL,
    stop_loss double precision NOT NULL,
    risk_reward double precision NOT NULL,
    reasoning text,
    ml_data text,
    raw_response text,
    result character varying(20),
    actual_pnl double precision,
    created_at timestamp without time zone,
    expires_at timestamp without time zone NOT NULL,
    closed_at timestamp without time zone
);


ALTER TABLE public.signals OWNER TO postgres;

--
-- Name: signals_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.signals_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.signals_id_seq OWNER TO postgres;

--
-- Name: signals_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.signals_id_seq OWNED BY public.signals.id;


--
-- Name: transactions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.transactions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    symbol character varying(20) NOT NULL,
    side character varying(10) NOT NULL,
    type character varying(20) NOT NULL,
    quantity double precision NOT NULL,
    price double precision NOT NULL,
    total double precision NOT NULL,
    order_id character varying(50),
    status character varying(20),
    created_at timestamp without time zone
);


ALTER TABLE public.transactions OWNER TO postgres;

--
-- Name: transactions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.transactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.transactions_id_seq OWNER TO postgres;

--
-- Name: transactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.transactions_id_seq OWNED BY public.transactions.id;


--
-- Name: trusted_devices; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.trusted_devices (
    id integer NOT NULL,
    user_id integer NOT NULL,
    device_id character varying(64) NOT NULL,
    user_agent character varying(500),
    ip_address character varying(45),
    created_at timestamp without time zone,
    expires_at timestamp without time zone NOT NULL
);


ALTER TABLE public.trusted_devices OWNER TO postgres;

--
-- Name: trusted_devices_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.trusted_devices_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.trusted_devices_id_seq OWNER TO postgres;

--
-- Name: trusted_devices_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.trusted_devices_id_seq OWNED BY public.trusted_devices.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying(255) NOT NULL,
    name character varying(100) NOT NULL,
    password_hash character varying(255) NOT NULL,
    totp_secret character varying(32),
    has_2fa boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    last_login timestamp without time zone
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: virtual_trades; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.virtual_trades (
    id integer NOT NULL,
    wallet_id integer NOT NULL,
    symbol character varying(20) NOT NULL,
    side character varying(10) NOT NULL,
    type character varying(20),
    strategy character varying(50),
    reason text,
    quantity double precision NOT NULL,
    price double precision NOT NULL,
    pnl double precision,
    created_at timestamp without time zone
);


ALTER TABLE public.virtual_trades OWNER TO postgres;

--
-- Name: virtual_trades_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.virtual_trades_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.virtual_trades_id_seq OWNER TO postgres;

--
-- Name: virtual_trades_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.virtual_trades_id_seq OWNED BY public.virtual_trades.id;


--
-- Name: virtual_wallets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.virtual_wallets (
    id integer NOT NULL,
    user_id integer NOT NULL,
    initial_capital double precision,
    balances text,
    created_at timestamp without time zone,
    reset_at timestamp without time zone
);


ALTER TABLE public.virtual_wallets OWNER TO postgres;

--
-- Name: virtual_wallets_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.virtual_wallets_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.virtual_wallets_id_seq OWNER TO postgres;

--
-- Name: virtual_wallets_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.virtual_wallets_id_seq OWNED BY public.virtual_wallets.id;


--
-- Name: whale_alerts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.whale_alerts (
    id integer NOT NULL,
    blockchain character varying(20),
    tx_hash character varying(128),
    amount double precision NOT NULL,
    amount_usd double precision NOT NULL,
    from_address character varying(128),
    to_address character varying(128),
    from_label character varying(100),
    to_label character varying(100),
    flow_type character varying(50),
    sentiment character varying(20),
    "timestamp" timestamp without time zone
);


ALTER TABLE public.whale_alerts OWNER TO postgres;

--
-- Name: whale_alerts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.whale_alerts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.whale_alerts_id_seq OWNER TO postgres;

--
-- Name: whale_alerts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.whale_alerts_id_seq OWNED BY public.whale_alerts.id;


--
-- Name: agent_trades id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_trades ALTER COLUMN id SET DEFAULT nextval('public.agent_trades_id_seq'::regclass);


--
-- Name: alerts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alerts ALTER COLUMN id SET DEFAULT nextval('public.alerts_id_seq'::regclass);


--
-- Name: funding_rate_history id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.funding_rate_history ALTER COLUMN id SET DEFAULT nextval('public.funding_rate_history_id_seq'::regclass);


--
-- Name: journal_entries id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.journal_entries ALTER COLUMN id SET DEFAULT nextval('public.journal_entries_id_seq'::regclass);


--
-- Name: order_book_snapshots id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_book_snapshots ALTER COLUMN id SET DEFAULT nextval('public.order_book_snapshots_id_seq'::regclass);


--
-- Name: p2p_rates id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.p2p_rates ALTER COLUMN id SET DEFAULT nextval('public.p2p_rates_id_seq'::regclass);


--
-- Name: signals id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.signals ALTER COLUMN id SET DEFAULT nextval('public.signals_id_seq'::regclass);


--
-- Name: transactions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transactions ALTER COLUMN id SET DEFAULT nextval('public.transactions_id_seq'::regclass);


--
-- Name: trusted_devices id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trusted_devices ALTER COLUMN id SET DEFAULT nextval('public.trusted_devices_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: virtual_trades id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.virtual_trades ALTER COLUMN id SET DEFAULT nextval('public.virtual_trades_id_seq'::regclass);


--
-- Name: virtual_wallets id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.virtual_wallets ALTER COLUMN id SET DEFAULT nextval('public.virtual_wallets_id_seq'::regclass);


--
-- Name: whale_alerts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.whale_alerts ALTER COLUMN id SET DEFAULT nextval('public.whale_alerts_id_seq'::regclass);


--
-- Data for Name: agent_trades; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.agent_trades (id, trade_id, symbol, side, entry_price, exit_price, pnl, signals_used, patterns_detected, created_at) FROM stdin;
\.


--
-- Data for Name: alerts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alerts (id, user_id, type, symbol, condition, target_value, is_active, triggered_at, created_at) FROM stdin;
\.


--
-- Data for Name: funding_rate_history; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.funding_rate_history (id, symbol, funding_rate, mark_price, index_price, open_interest, "timestamp", next_funding_time) FROM stdin;
1	BTCUSDT	-0.00010086	64088.16895652	64139.22478261	\N	2026-02-06 01:23:19.363693	\N
2	ETHUSDT	-0.00041567	1889.33	1890.52069767	\N	2026-02-06 01:23:19.860237	\N
3	SOLUSDT	-0.00031229	76.83044399	76.93124172	\N	2026-02-06 01:23:20.361362	\N
4	BNBUSDT	4.362e-05	622.21210563	621.89502548	\N	2026-02-06 01:23:20.863951	\N
5	BTCUSDT	-0.00010685	64119.8	64135.07826087	\N	2026-02-06 01:33:21.740281	\N
6	ETHUSDT	-0.00040511	1896.77402326	1897.72627907	\N	2026-02-06 01:33:22.251665	\N
7	SOLUSDT	-0.00032724	77.42	77.46133161	\N	2026-02-06 01:33:22.757253	\N
8	BNBUSDT	4.654e-05	621.89274112	621.49704479	\N	2026-02-06 01:33:23.264306	\N
9	BTCUSDT	-0.00011135	64534.3	64565.7073913	\N	2026-02-06 01:43:25.632726	\N
10	ETHUSDT	-0.00039451	1918.0652671	1918.48232558	\N	2026-02-06 01:43:26.132494	\N
11	SOLUSDT	-0.00034775	78.22362336	78.31245992	\N	2026-02-06 01:43:26.633711	\N
12	BNBUSDT	4.686e-05	625.8	625.37998032	\N	2026-02-06 01:43:27.133225	\N
13	BTCUSDT	-0.00011562	65206.3	65241.19434783	\N	2026-02-06 01:53:22.734647	\N
14	ETHUSDT	-0.00038343	1924.79785271	1926.29604651	\N	2026-02-06 01:53:23.265744	\N
15	SOLUSDT	-0.0003674	79.03843299	79.15151157	\N	2026-02-06 01:53:23.791413	\N
16	BNBUSDT	4.675e-05	625.98	625.90556466	\N	2026-02-06 01:53:24.324378	\N
17	BTCUSDT	-0.00012202	65451.7	65510.15434783	\N	2026-02-06 02:03:25.866158	\N
18	ETHUSDT	-0.00037871	1931.54	1932.34930233	\N	2026-02-06 02:03:26.461886	\N
19	SOLUSDT	-0.00039125	79.49	79.60593006	\N	2026-02-06 02:03:27.055642	\N
20	BNBUSDT	4.498e-05	629.93226414	629.78396027	\N	2026-02-06 02:03:27.649539	\N
21	BTCUSDT	-0.00012805	64737.5	64749.46978261	\N	2026-02-06 02:13:31.080766	\N
22	ETHUSDT	-0.00037006	1912.9152206	1913.29790698	\N	2026-02-06 02:13:31.676006	\N
23	SOLUSDT	-0.00042211	78.07140899	78.17638275	\N	2026-02-06 02:13:32.271922	\N
24	BNBUSDT	4.43e-05	625.06	624.81096027	\N	2026-02-06 02:13:32.872245	\N
25	BTCUSDT	-0.00012987	64326.2	64355.74065217	\N	2026-02-06 02:23:38.319033	\N
26	ETHUSDT	-0.00035986	1893.93	1894.8172093	\N	2026-02-06 02:23:39.279617	\N
27	SOLUSDT	-0.00043535	76.97	77.05269807	\N	2026-02-06 02:23:39.804483	\N
28	BNBUSDT	4.497e-05	620.16210859	619.8129437	\N	2026-02-06 02:23:40.325185	\N
29	BTCUSDT	-0.00013119	64901.35503623	64929.58347826	\N	2026-02-06 02:33:49.1414	\N
30	ETHUSDT	-0.00034904	1922.79325581	1923.30813953	\N	2026-02-06 02:33:49.667861	\N
31	SOLUSDT	-0.00044134	77.83449019	77.90141077	\N	2026-02-06 02:33:50.193068	\N
32	BNBUSDT	4.741e-05	625.91824303	625.39467637	\N	2026-02-06 02:33:51.137866	\N
33	BTCUSDT	-0.00013699	65289.2	65311.59826087	\N	2026-02-06 02:43:59.324264	\N
34	ETHUSDT	-0.0003388	1921.65	1922.13674419	\N	2026-02-06 02:43:59.851106	\N
35	SOLUSDT	-0.00044429	78.02428312	78.10184537	\N	2026-02-06 02:44:00.802555	\N
36	BNBUSDT	4.522e-05	628.34	628.02129207	\N	2026-02-06 02:44:01.327568	\N
37	BTCUSDT	-0.00013813	65060.76000725	65109.83956522	\N	2026-02-06 02:46:12.017924	\N
38	ETHUSDT	-0.00033616	1914.27590698	1915.6727907	\N	2026-02-06 02:46:12.542713	\N
39	SOLUSDT	-0.00044545	77.45	77.52165204	\N	2026-02-06 02:46:13.067562	\N
40	BNBUSDT	4.447e-05	625.37	625.17684584	\N	2026-02-06 02:46:13.593637	\N
41	BTCUSDT	-0.00014026	64704.9	64751.56	\N	2026-02-06 02:56:14.52585	\N
42	ETHUSDT	-0.00032658	1899.34372494	1900.79395349	\N	2026-02-06 02:56:14.992212	\N
43	SOLUSDT	-0.00044444	76.4320042	76.43976342	\N	2026-02-06 02:56:15.45735	\N
44	BNBUSDT	4.273e-05	620.88532286	620.65446301	\N	2026-02-06 02:56:15.921386	\N
45	BTCUSDT	-0.00014189	64892.4	64939.89804348	\N	2026-02-06 03:06:17.214637	\N
46	ETHUSDT	-0.00031522	1907.36	1908.26348837	\N	2026-02-06 03:06:17.735367	\N
47	SOLUSDT	-0.00044253	76.84	76.914723	\N	2026-02-06 03:06:18.261232	\N
48	BNBUSDT	4.195e-05	623.72	623.53254685	\N	2026-02-06 03:06:18.787768	\N
49	BTCUSDT	-0.00014325	64543.9	64565.075	\N	2026-02-06 03:16:20.012452	\N
50	ETHUSDT	-0.00029748	1897.12308915	1897.82488372	\N	2026-02-06 03:16:20.463106	\N
51	SOLUSDT	-0.00044084	76.56408341	76.6091653	\N	2026-02-06 03:16:20.90857	\N
52	BNBUSDT	3.891e-05	618.97	618.67558014	\N	2026-02-06 03:16:21.355579	\N
53	BTCUSDT	-0.00014241	64521.79078986	64564.08130435	\N	2026-02-06 03:25:20.003347	\N
54	ETHUSDT	-0.00028508	1890.61	1891.05860465	\N	2026-02-06 03:25:20.514563	\N
55	SOLUSDT	-0.00043694	76.13	76.17491416	\N	2026-02-06 03:25:21.033976	\N
56	BNBUSDT	3.847e-05	618.72602028	618.31730059	\N	2026-02-06 03:25:21.555503	\N
57	BTCUSDT	-0.00014184	64828.30672464	64866.58695652	\N	2026-02-06 03:35:22.968853	\N
58	ETHUSDT	-0.00027061	1902.34855039	1903.29069767	\N	2026-02-06 03:35:23.478034	\N
59	SOLUSDT	-0.00042909	76.8428822	76.89386922	\N	2026-02-06 03:35:23.983425	\N
60	BNBUSDT	4.17e-05	620.6	620.40466397	\N	2026-02-06 03:35:24.484285	\N
61	BTCUSDT	-0.00014205	64458.51407971	64494.32195652	\N	2026-02-06 03:45:31.979743	\N
62	ETHUSDT	-0.00025604	1889.86723256	1890.70348837	\N	2026-02-06 03:45:32.501023	\N
63	SOLUSDT	-0.0004208	76.21136976	76.2534637	\N	2026-02-06 03:45:33.459863	\N
64	BNBUSDT	4.259e-05	616.13	615.67570037	\N	2026-02-06 03:45:33.995017	\N
65	BTCUSDT	-0.00013856	64046.22592029	64064.99521739	\N	2026-02-06 03:55:37.810048	\N
66	ETHUSDT	-0.0002403	1887.39	1887.66325581	\N	2026-02-06 03:55:38.387915	\N
67	SOLUSDT	-0.00040929	76.4	76.42102384	\N	2026-02-06 03:55:38.972388	\N
68	BNBUSDT	4.488e-05	615.30480337	614.79291534	\N	2026-02-06 03:55:39.560496	\N
69	BTCUSDT	-0.00013172	64256.98293103	64293.7376087	\N	2026-02-06 04:05:41.588701	\N
70	ETHUSDT	-0.00022206	1891.61119888	1892.2455814	\N	2026-02-06 04:05:42.529251	\N
71	SOLUSDT	-0.00039531	76.32621346	76.37782198	\N	2026-02-06 04:05:43.053977	\N
72	BNBUSDT	5.041e-05	616.64	616.51648715	\N	2026-02-06 04:05:44.001111	\N
73	BTCUSDT	-0.00012773	64447.86213768	64481.56065217	\N	2026-02-06 04:15:48.178772	\N
74	ETHUSDT	-0.00020653	1900.33496124	1901.20697674	\N	2026-02-06 04:15:48.753409	\N
75	SOLUSDT	-0.00038517	76.68720992	76.74877721	\N	2026-02-06 04:15:49.334472	\N
76	BNBUSDT	4.777e-05	620.05	619.9706494	\N	2026-02-06 04:15:49.92364	\N
\.


--
-- Data for Name: journal_entries; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.journal_entries (id, user_id, symbol, side, entry_price, exit_price, pnl, mood, strategy, notes, lessons, rating, created_at) FROM stdin;
\.


--
-- Data for Name: order_book_snapshots; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.order_book_snapshots (id, symbol, best_bid, best_ask, spread, bids_json, asks_json, bid_volume_10, ask_volume_10, "timestamp") FROM stdin;
1	BTCUSDT	64130.03	64130.04	0.010000000002037268	[['64130.03000000', '0.06174000'], ['64130.02000000', '0.00009000'], ['64129.35000000', '0.00018000'], ['64129.34000000', '0.00008000'], ['64127.21000000', '0.00039000'], ['64126.85000000', '0.00008000'], ['64126.49000000', '0.01765000'], ['64126.16000000', '0.00018000'], ['64126.15000000', '0.69460000'], ['64125.38000000', '0.00010000'], ['64125.08000000', '0.00018000'], ['64125.07000000', '0.00026000'], ['64125.06000000', '0.00509000'], ['64125.00000000', '0.00035000'], ['64124.93000000', '0.18302000'], ['64124.36000000', '0.02322000'], ['64124.22000000', '0.00250000'], ['64123.62000000', '0.00009000'], ['64123.61000000', '0.24758000'], ['64123.20000000', '0.00008000']]	[['64130.04000000', '0.64796000'], ['64130.05000000', '0.00009000'], ['64130.38000000', '0.00027000'], ['64130.39000000', '0.00027000'], ['64130.50000000', '0.00008000'], ['64130.75000000', '0.00008000'], ['64131.11000000', '0.00018000'], ['64131.73000000', '0.02102000'], ['64131.74000000', '0.00018000'], ['64131.84000000', '0.00009000'], ['64131.99000000', '0.00008000'], ['64132.00000000', '0.03882000'], ['64132.97000000', '0.09674000'], ['64133.22000000', '0.00008000'], ['64133.74000000', '0.00008000'], ['64133.80000000', '0.00300000'], ['64134.15000000', '0.00008000'], ['64134.68000000', '0.00250000'], ['64134.72000000', '0.00018000'], ['64134.73000000', '0.00020000']]	\N	\N	2026-02-06 01:23:19.571618
2	ETHUSDT	1890.79	1890.8	0.009999999999990905	[['1890.79000000', '1.61970000'], ['1890.72000000', '0.00610000'], ['1890.70000000', '0.02040000'], ['1890.63000000', '0.00610000'], ['1890.61000000', '0.00290000'], ['1890.60000000', '0.01090000'], ['1890.59000000', '0.00290000'], ['1890.58000000', '0.01390000'], ['1890.57000000', '0.06370000'], ['1890.56000000', '0.00560000'], ['1890.54000000', '0.00320000'], ['1890.51000000', '0.05950000'], ['1890.50000000', '0.06270000'], ['1890.49000000', '0.00540000'], ['1890.48000000', '0.05270000'], ['1890.45000000', '0.00320000'], ['1890.43000000', '3.15270000'], ['1890.42000000', '13.22130000'], ['1890.41000000', '5.30120000'], ['1890.40000000', '0.41350000']]	[['1890.80000000', '10.51480000'], ['1890.90000000', '0.00270000'], ['1890.96000000', '0.05000000'], ['1890.98000000', '0.00800000'], ['1890.99000000', '3.45470000'], ['1891.00000000', '0.00270000'], ['1891.01000000', '3.10850000'], ['1891.03000000', '15.92160000'], ['1891.05000000', '0.00940000'], ['1891.08000000', '0.37760000'], ['1891.09000000', '0.07080000'], ['1891.10000000', '0.00270000'], ['1891.13000000', '5.30130000'], ['1891.15000000', '3.20200000'], ['1891.16000000', '0.63490000'], ['1891.17000000', '0.00850000'], ['1891.18000000', '16.86530000'], ['1891.19000000', '0.00270000'], ['1891.20000000', '0.05840000'], ['1891.21000000', '0.10000000']]	\N	\N	2026-02-06 01:23:20.068654
3	SOLUSDT	76.92	76.93	0.010000000000005116	[['76.92000000', '149.64500000'], ['76.91000000', '28.03600000'], ['76.90000000', '35.72000000'], ['76.89000000', '1431.95400000'], ['76.88000000', '1225.77000000'], ['76.87000000', '1178.32700000'], ['76.86000000', '1269.62100000'], ['76.85000000', '694.43700000'], ['76.84000000', '1003.50900000'], ['76.83000000', '530.67800000'], ['76.82000000', '366.81800000'], ['76.81000000', '973.85500000'], ['76.80000000', '811.92600000'], ['76.79000000', '307.84000000'], ['76.78000000', '272.02300000'], ['76.77000000', '660.13500000'], ['76.76000000', '109.43400000'], ['76.75000000', '851.68600000'], ['76.74000000', '129.43100000'], ['76.73000000', '227.45700000']]	[['76.93000000', '270.74000000'], ['76.94000000', '870.98700000'], ['76.95000000', '984.87700000'], ['76.96000000', '1385.02700000'], ['76.97000000', '1148.64400000'], ['76.98000000', '1204.74900000'], ['76.99000000', '490.85800000'], ['77.00000000', '346.44700000'], ['77.01000000', '748.57800000'], ['77.02000000', '1259.53900000'], ['77.03000000', '236.73100000'], ['77.04000000', '807.88000000'], ['77.05000000', '602.56900000'], ['77.06000000', '230.57300000'], ['77.07000000', '96.60800000'], ['77.08000000', '514.35900000'], ['77.09000000', '150.36300000'], ['77.10000000', '588.61900000'], ['77.11000000', '492.93300000'], ['77.12000000', '796.39300000']]	\N	\N	2026-02-06 01:23:20.570163
4	BNBUSDT	622.02	622.03	0.009999999999990905	[['622.02000000', '12.38400000'], ['622.01000000', '3.05100000'], ['622.00000000', '4.83900000'], ['621.99000000', '1.71400000'], ['621.98000000', '10.08700000'], ['621.97000000', '2.35000000'], ['621.96000000', '4.03700000'], ['621.95000000', '3.58200000'], ['621.94000000', '2.24100000'], ['621.93000000', '1.72900000'], ['621.92000000', '1.72200000'], ['621.91000000', '0.37000000'], ['621.90000000', '0.00900000'], ['621.89000000', '0.01700000'], ['621.88000000', '2.45900000'], ['621.87000000', '10.40500000'], ['621.86000000', '1.81700000'], ['621.84000000', '3.06700000'], ['621.83000000', '0.01700000'], ['621.82000000', '1.45700000']]	[['622.03000000', '0.07100000'], ['622.04000000', '0.01800000'], ['622.05000000', '0.02700000'], ['622.06000000', '0.01800000'], ['622.07000000', '0.01800000'], ['622.08000000', '0.03500000'], ['622.09000000', '0.00900000'], ['622.10000000', '0.00900000'], ['622.11000000', '0.03100000'], ['622.12000000', '0.01700000'], ['622.14000000', '1.41400000'], ['622.15000000', '0.02600000'], ['622.16000000', '0.01900000'], ['622.17000000', '6.67800000'], ['622.18000000', '4.84600000'], ['622.20000000', '2.78500000'], ['622.21000000', '0.44800000'], ['622.23000000', '2.46800000'], ['622.24000000', '1.83500000'], ['622.25000000', '0.07900000']]	\N	\N	2026-02-06 01:23:21.07249
5	BTCUSDT	64170.64	64170.65	0.010000000002037268	[['64170.64000000', '1.34392000'], ['64170.63000000', '0.00009000'], ['64169.99000000', '0.07027000'], ['64168.09000000', '0.08102000'], ['64168.08000000', '0.00250000'], ['64168.05000000', '0.08381000'], ['64168.04000000', '0.38098000'], ['64167.00000000', '0.00035000'], ['64166.99000000', '0.01407000'], ['64166.79000000', '0.00018000'], ['64166.46000000', '0.15898000'], ['64165.52000000', '0.02381000'], ['64165.50000000', '0.00250000'], ['64165.12000000', '1.63366000'], ['64165.11000000', '2.24568000'], ['64163.41000000', '0.15898000'], ['64163.39000000', '0.40790000'], ['64163.35000000', '0.00008000'], ['64163.00000000', '0.04760000'], ['64162.64000000', '0.00016000']]	[['64170.65000000', '0.00513000'], ['64170.66000000', '0.00009000'], ['64171.45000000', '0.00016000'], ['64172.88000000', '0.00009000'], ['64173.00000000', '0.00008000'], ['64173.69000000', '0.00178000'], ['64173.97000000', '0.00015000'], ['64174.07000000', '0.00008000'], ['64174.25000000', '0.00318000'], ['64174.30000000', '0.00008000'], ['64174.35000000', '0.00017000'], ['64174.76000000', '0.00008000'], ['64174.84000000', '0.00008000'], ['64174.85000000', '0.00080000'], ['64175.10000000', '0.00008000'], ['64175.91000000', '0.00018000'], ['64175.92000000', '0.00018000'], ['64176.60000000', '0.00008000'], ['64176.67000000', '0.00031000'], ['64176.88000000', '0.00316000']]	\N	\N	2026-02-06 01:33:21.951469
6	ETHUSDT	1897.29	1897.3	0.009999999999990905	[['1897.29000000', '0.02520000'], ['1897.26000000', '0.64670000'], ['1897.25000000', '0.00530000'], ['1897.23000000', '0.00560000'], ['1897.22000000', '0.00620000'], ['1897.20000000', '0.01120000'], ['1897.19000000', '0.00560000'], ['1897.18000000', '0.00350000'], ['1897.16000000', '0.00270000'], ['1897.15000000', '0.00530000'], ['1897.12000000', '0.00270000'], ['1897.11000000', '0.00720000'], ['1897.10000000', '0.00830000'], ['1897.09000000', '0.00530000'], ['1897.06000000', '0.00530000'], ['1897.05000000', '0.00270000'], ['1897.02000000', '0.01400000'], ['1897.01000000', '0.06530000'], ['1897.00000000', '0.00270000'], ['1896.99000000', '0.00270000']]	[['1897.30000000', '16.51120000'], ['1897.34000000', '0.30000000'], ['1897.35000000', '1.12680000'], ['1897.38000000', '0.05810000'], ['1897.39000000', '0.00290000'], ['1897.40000000', '0.00560000'], ['1897.43000000', '0.00290000'], ['1897.44000000', '0.00290000'], ['1897.46000000', '0.00290000'], ['1897.47000000', '0.00290000'], ['1897.50000000', '5.27760000'], ['1897.55000000', '0.03110000'], ['1897.57000000', '3.15000000'], ['1897.60000000', '5.27760000'], ['1897.61000000', '0.00530000'], ['1897.63000000', '0.01610000'], ['1897.67000000', '0.11790000'], ['1897.68000000', '0.02500000'], ['1897.69000000', '0.00400000'], ['1897.70000000', '0.00270000']]	\N	\N	2026-02-06 01:33:22.455826
7	SOLUSDT	77.54	77.55	0.009999999999990905	[['77.54000000', '209.59200000'], ['77.53000000', '72.12700000'], ['77.52000000', '95.20100000'], ['77.51000000', '821.52800000'], ['77.50000000', '989.66500000'], ['77.49000000', '1199.65300000'], ['77.48000000', '770.52800000'], ['77.47000000', '2398.88700000'], ['77.46000000', '1359.42000000'], ['77.45000000', '814.83400000'], ['77.44000000', '740.15000000'], ['77.43000000', '838.86700000'], ['77.42000000', '291.05100000'], ['77.41000000', '1787.63600000'], ['77.40000000', '498.98100000'], ['77.39000000', '230.22800000'], ['77.38000000', '76.06100000'], ['77.37000000', '613.40300000'], ['77.36000000', '103.41900000'], ['77.35000000', '886.87000000']]	[['77.55000000', '137.94000000'], ['77.56000000', '47.64800000'], ['77.57000000', '719.45900000'], ['77.58000000', '846.58700000'], ['77.59000000', '909.75000000'], ['77.60000000', '907.95200000'], ['77.61000000', '142.94500000'], ['77.62000000', '781.13500000'], ['77.63000000', '99.88300000'], ['77.64000000', '229.75200000'], ['77.65000000', '532.89200000'], ['77.66000000', '754.57200000'], ['77.67000000', '95.80600000'], ['77.68000000', '104.13300000'], ['77.69000000', '225.98600000'], ['77.70000000', '485.47600000'], ['77.71000000', '227.86100000'], ['77.72000000', '167.86500000'], ['77.73000000', '989.19500000'], ['77.74000000', '1364.34700000']]	\N	\N	2026-02-06 01:33:22.964848
8	BNBUSDT	621.73	621.74	0.009999999999990905	[['621.73000000', '1.54100000'], ['621.72000000', '0.07300000'], ['621.70000000', '1.62700000'], ['621.69000000', '1.62700000'], ['621.67000000', '0.00900000'], ['621.66000000', '0.00900000'], ['621.64000000', '0.01700000'], ['621.62000000', '2.41200000'], ['621.61000000', '3.32100000'], ['621.60000000', '0.54500000'], ['621.59000000', '1.11400000'], ['621.58000000', '1.80000000'], ['621.57000000', '5.34700000'], ['621.56000000', '0.51400000'], ['621.54000000', '1.02000000'], ['621.51000000', '0.01700000'], ['621.50000000', '2.18400000'], ['621.49000000', '4.73400000'], ['621.48000000', '2.48800000'], ['621.47000000', '0.01700000']]	[['621.74000000', '6.53000000'], ['621.75000000', '4.43500000'], ['621.76000000', '1.62700000'], ['621.77000000', '1.62700000'], ['621.78000000', '3.78600000'], ['621.79000000', '0.02200000'], ['621.80000000', '0.01000000'], ['621.81000000', '0.00900000'], ['621.82000000', '0.35200000'], ['621.83000000', '4.73400000'], ['621.84000000', '0.05300000'], ['621.85000000', '0.03000000'], ['621.87000000', '0.83100000'], ['621.88000000', '0.01000000'], ['621.89000000', '2.72400000'], ['621.90000000', '7.75600000'], ['621.91000000', '0.01300000'], ['621.93000000', '0.02600000'], ['621.95000000', '4.16600000'], ['621.96000000', '1.83600000']]	\N	\N	2026-02-06 01:33:23.476469
9	BTCUSDT	64567.98	64567.99	0.00999999999476131	[['64567.98000000', '0.13607000'], ['64567.97000000', '0.00009000'], ['64566.40000000', '0.00009000'], ['64566.07000000', '0.00008000'], ['64564.99000000', '0.00008000'], ['64564.85000000', '0.00008000'], ['64563.46000000', '0.00309000'], ['64562.53000000', '0.00018000'], ['64562.12000000', '0.00018000'], ['64561.25000000', '0.00018000'], ['64561.24000000', '0.07461000'], ['64561.23000000', '0.24935000'], ['64561.20000000', '0.00008000'], ['64559.93000000', '0.00016000'], ['64559.63000000', '0.00018000'], ['64559.62000000', '0.01633000'], ['64559.32000000', '0.00258000'], ['64559.24000000', '0.00009000'], ['64559.22000000', '0.00010000'], ['64559.19000000', '0.00018000']]	[['64567.99000000', '0.59059000'], ['64568.00000000', '0.00036000'], ['64568.51000000', '0.00027000'], ['64572.50000000', '0.13899000'], ['64572.51000000', '0.00309000'], ['64572.68000000', '0.19356000'], ['64572.69000000', '0.14510000'], ['64573.70000000', '0.51186000'], ['64573.81000000', '0.01000000'], ['64573.84000000', '0.01665000'], ['64573.92000000', '0.00018000'], ['64573.93000000', '0.05970000'], ['64574.44000000', '1.10033000'], ['64574.45000000', '0.24768000'], ['64574.84000000', '0.00012000'], ['64574.89000000', '0.06979000'], ['64575.26000000', '0.02278000'], ['64575.31000000', '0.10000000'], ['64575.73000000', '0.00016000'], ['64576.91000000', '3.39365000']]	\N	\N	2026-02-06 01:43:25.840401
10	ETHUSDT	1918.08	1918.09	0.009999999999990905	[['1918.08000000', '9.44610000'], ['1918.04000000', '0.00690000'], ['1918.03000000', '0.00290000'], ['1918.02000000', '0.00290000'], ['1918.00000000', '0.00830000'], ['1917.99000000', '0.00610000'], ['1917.96000000', '5.21320000'], ['1917.95000000', '0.00290000'], ['1917.94000000', '0.64530000'], ['1917.92000000', '0.00290000'], ['1917.91000000', '0.00560000'], ['1917.90000000', '2.75710000'], ['1917.89000000', '0.00530000'], ['1917.88000000', '0.06030000'], ['1917.87000000', '0.00270000'], ['1917.85000000', '7.96490000'], ['1917.84000000', '3.16080000'], ['1917.81000000', '0.06590000'], ['1917.80000000', '0.00270000'], ['1917.79000000', '0.00530000']]	[['1918.09000000', '1.43750000'], ['1918.10000000', '0.00560000'], ['1918.11000000', '0.00290000'], ['1918.15000000', '0.00850000'], ['1918.16000000', '0.23040000'], ['1918.19000000', '0.00290000'], ['1918.20000000', '0.00560000'], ['1918.21000000', '0.00290000'], ['1918.22000000', '0.00290000'], ['1918.26000000', '0.00850000'], ['1918.27000000', '0.17670000'], ['1918.28000000', '0.00530000'], ['1918.30000000', '0.00670000'], ['1918.32000000', '0.00530000'], ['1918.34000000', '0.00830000'], ['1918.35000000', '0.00830000'], ['1918.36000000', '15.66580000'], ['1918.38000000', '1.68660000'], ['1918.40000000', '0.00270000'], ['1918.42000000', '3.15000000']]	\N	\N	2026-02-06 01:43:26.341899
11	SOLUSDT	78.28	78.29	0.010000000000005116	[['78.28000000', '19.48200000'], ['78.27000000', '28.66900000'], ['78.26000000', '341.46900000'], ['78.25000000', '287.93500000'], ['78.24000000', '279.15600000'], ['78.23000000', '560.96600000'], ['78.22000000', '1465.37600000'], ['78.21000000', '1294.51400000'], ['78.20000000', '976.41700000'], ['78.19000000', '1434.58100000'], ['78.18000000', '593.10700000'], ['78.17000000', '702.25600000'], ['78.16000000', '1035.58300000'], ['78.15000000', '277.20700000'], ['78.14000000', '785.35000000'], ['78.13000000', '395.22000000'], ['78.12000000', '30.49800000'], ['78.11000000', '61.79100000'], ['78.10000000', '515.01200000'], ['78.09000000', '27.19500000']]	[['78.29000000', '842.58200000'], ['78.30000000', '904.08100000'], ['78.31000000', '499.16100000'], ['78.32000000', '777.55500000'], ['78.33000000', '401.66300000'], ['78.34000000', '400.73000000'], ['78.35000000', '389.40000000'], ['78.36000000', '1139.20700000'], ['78.37000000', '375.83100000'], ['78.38000000', '27.36500000'], ['78.39000000', '870.43400000'], ['78.40000000', '165.65100000'], ['78.41000000', '541.62400000'], ['78.42000000', '566.68900000'], ['78.43000000', '49.44800000'], ['78.44000000', '267.26600000'], ['78.45000000', '444.06300000'], ['78.46000000', '222.21700000'], ['78.47000000', '540.81900000'], ['78.48000000', '28.21900000']]	\N	\N	2026-02-06 01:43:26.840204
12	BNBUSDT	625.06	625.07	0.010000000000104592	[['625.06000000', '0.06100000'], ['625.05000000', '0.01800000'], ['625.04000000', '1.06000000'], ['625.03000000', '0.03500000'], ['625.02000000', '0.05300000'], ['625.01000000', '0.43300000'], ['625.00000000', '0.00900000'], ['624.99000000', '0.02600000'], ['624.98000000', '1.82600000'], ['624.97000000', '0.25300000'], ['624.96000000', '0.46800000'], ['624.95000000', '0.83000000'], ['624.94000000', '4.82500000'], ['624.93000000', '0.01200000'], ['624.92000000', '0.01000000'], ['624.91000000', '1.81700000'], ['624.90000000', '0.04500000'], ['624.89000000', '0.71500000'], ['624.88000000', '0.01000000'], ['624.87000000', '2.08300000']]	[['625.07000000', '4.72600000'], ['625.08000000', '1.09100000'], ['625.09000000', '1.08200000'], ['625.10000000', '1.04200000'], ['625.11000000', '1.57300000'], ['625.12000000', '1.60300000'], ['625.13000000', '1.56500000'], ['625.14000000', '1.05000000'], ['625.15000000', '1.05900000'], ['625.16000000', '1.04200000'], ['625.17000000', '2.43100000'], ['625.19000000', '0.01700000'], ['625.20000000', '1.36200000'], ['625.21000000', '0.01200000'], ['625.22000000', '0.00900000'], ['625.23000000', '0.02500000'], ['625.25000000', '0.01700000'], ['625.26000000', '0.00800000'], ['625.27000000', '0.01200000'], ['625.28000000', '1.81700000']]	\N	\N	2026-02-06 01:43:27.338794
13	BTCUSDT	65222.75	65222.76	0.010000000002037268	[['65222.75000000', '0.29767000'], ['65222.74000000', '0.00009000'], ['65221.85000000', '0.00008000'], ['65220.34000000', '0.00012000'], ['65220.07000000', '0.00031000'], ['65220.00000000', '0.00008000'], ['65219.17000000', '0.00018000'], ['65219.16000000', '0.00045000'], ['65219.15000000', '0.00036000'], ['65219.05000000', '0.00017000'], ['65218.85000000', '0.00267000'], ['65218.20000000', '0.00008000'], ['65217.95000000', '0.00266000'], ['65217.23000000', '0.00008000'], ['65216.36000000', '0.00010000'], ['65216.14000000', '0.00018000'], ['65216.13000000', '0.00036000'], ['65216.12000000', '0.11665000'], ['65216.05000000', '0.00016000'], ['65215.78000000', '0.00018000']]	[['65222.76000000', '0.73197000'], ['65222.77000000', '0.00009000'], ['65224.68000000', '0.01421000'], ['65225.50000000', '0.00008000'], ['65226.92000000', '0.11764000'], ['65226.93000000', '0.03656000'], ['65226.94000000', '0.10604000'], ['65226.96000000', '0.00009000'], ['65228.65000000', '0.00040000'], ['65229.15000000', '0.00016000'], ['65230.58000000', '0.06271000'], ['65230.59000000', '0.10315000'], ['65230.60000000', '0.02318000'], ['65230.90000000', '0.00016000'], ['65231.33000000', '0.00018000'], ['65231.34000000', '0.08120000'], ['65231.53000000', '0.00250000'], ['65231.74000000', '0.00250000'], ['65232.80000000', '0.00008000'], ['65232.81000000', '1.89466000']]	\N	\N	2026-02-06 01:53:23.032789
14	ETHUSDT	1924.81	1924.82	0.009999999999990905	[['1924.81000000', '0.01050000'], ['1924.80000000', '0.00950000'], ['1924.78000000', '0.00560000'], ['1924.77000000', '0.00350000'], ['1924.76000000', '0.00560000'], ['1924.75000000', '0.00350000'], ['1924.71000000', '0.00290000'], ['1924.70000000', '0.00260000'], ['1924.68000000', '0.00560000'], ['1924.67000000', '0.06000000'], ['1924.66000000', '0.00560000'], ['1924.65000000', '0.00830000'], ['1924.63000000', '0.00290000'], ['1924.62000000', '0.01050000'], ['1924.61000000', '0.00390000'], ['1924.60000000', '0.00260000'], ['1924.59000000', '0.01080000'], ['1924.57000000', '0.00270000'], ['1924.56000000', '0.05000000'], ['1924.53000000', '0.00530000']]	[['1924.82000000', '23.93590000'], ['1924.85000000', '0.00260000'], ['1924.87000000', '0.00260000'], ['1924.88000000', '0.00260000'], ['1924.89000000', '0.00260000'], ['1924.90000000', '0.00260000'], ['1924.91000000', '1.74910000'], ['1924.93000000', '0.31290000'], ['1924.96000000', '7.07260000'], ['1924.97000000', '4.19040000'], ['1924.99000000', '0.00260000'], ['1925.00000000', '0.00260000'], ['1925.01000000', '20.75950000'], ['1925.02000000', '0.00540000'], ['1925.03000000', '2.76640000'], ['1925.05000000', '4.89260000'], ['1925.06000000', '0.00260000'], ['1925.09000000', '0.00390000'], ['1925.10000000', '3.04780000'], ['1925.12000000', '5.23970000']]	\N	\N	2026-02-06 01:53:23.558447
15	SOLUSDT	79.07	79.08	0.010000000000005116	[['79.07000000', '357.54000000'], ['79.06000000', '168.54700000'], ['79.05000000', '248.22000000'], ['79.04000000', '700.32300000'], ['79.03000000', '602.76900000'], ['79.02000000', '896.87900000'], ['79.01000000', '715.05700000'], ['79.00000000', '1050.24700000'], ['78.99000000', '867.16800000'], ['78.98000000', '105.95000000'], ['78.97000000', '344.85300000'], ['78.96000000', '557.31000000'], ['78.95000000', '255.68400000'], ['78.94000000', '697.45000000'], ['78.93000000', '550.27600000'], ['78.92000000', '101.56900000'], ['78.91000000', '243.10700000'], ['78.90000000', '112.15500000'], ['78.89000000', '253.33800000'], ['78.88000000', '893.95500000']]	[['79.08000000', '29.83300000'], ['79.09000000', '57.28800000'], ['79.10000000', '334.07000000'], ['79.11000000', '413.69700000'], ['79.12000000', '471.63100000'], ['79.13000000', '435.32100000'], ['79.14000000', '830.22700000'], ['79.15000000', '884.53200000'], ['79.16000000', '431.40400000'], ['79.17000000', '470.07600000'], ['79.18000000', '81.74400000'], ['79.19000000', '281.51000000'], ['79.20000000', '377.84400000'], ['79.21000000', '172.15400000'], ['79.22000000', '50.16900000'], ['79.23000000', '590.98100000'], ['79.24000000', '206.83500000'], ['79.25000000', '1710.07000000'], ['79.26000000', '377.77900000'], ['79.27000000', '30.22200000']]	\N	\N	2026-02-06 01:53:24.090616
16	BNBUSDT	625.59	625.6	0.009999999999990905	[['625.59000000', '4.91900000'], ['625.58000000', '1.09900000'], ['625.57000000', '1.02800000'], ['625.56000000', '0.01700000'], ['625.55000000', '1.64000000'], ['625.53000000', '6.38600000'], ['625.52000000', '3.42400000'], ['625.51000000', '1.59500000'], ['625.50000000', '0.02700000'], ['625.49000000', '1.07200000'], ['625.48000000', '0.01000000'], ['625.47000000', '0.01700000'], ['625.46000000', '0.35600000'], ['625.45000000', '4.80300000'], ['625.44000000', '0.04500000'], ['625.43000000', '1.80800000'], ['625.41000000', '0.01700000'], ['625.40000000', '0.02200000'], ['625.39000000', '6.14600000'], ['625.38000000', '0.03500000']]	[['625.60000000', '0.25000000'], ['625.61000000', '0.05500000'], ['625.62000000', '0.06300000'], ['625.65000000', '0.00800000'], ['625.66000000', '0.01200000'], ['625.67000000', '0.01700000'], ['625.68000000', '0.61800000'], ['625.69000000', '0.60000000'], ['625.70000000', '1.81700000'], ['625.71000000', '0.02500000'], ['625.72000000', '0.01200000'], ['625.74000000', '0.63500000'], ['625.77000000', '1.82500000'], ['625.78000000', '0.01200000'], ['625.79000000', '4.81800000'], ['625.80000000', '0.04500000'], ['625.83000000', '0.02500000'], ['625.84000000', '2.02200000'], ['625.85000000', '2.04100000'], ['625.86000000', '1.83500000']]	\N	\N	2026-02-06 01:53:24.622173
17	BTCUSDT	65500.33	65500.34	0.00999999999476131	[['65500.33000000', '0.44225000'], ['65500.32000000', '0.00036000'], ['65500.31000000', '0.00027000'], ['65499.84000000', '0.00009000'], ['65499.83000000', '0.00352000'], ['65499.29000000', '0.00008000'], ['65499.25000000', '0.00008000'], ['65498.12000000', '0.00012000'], ['65497.61000000', '0.00009000'], ['65495.80000000', '0.00018000'], ['65495.78000000', '0.00009000'], ['65495.60000000', '0.00008000'], ['65495.26000000', '0.00017000'], ['65495.24000000', '0.00300000'], ['65494.72000000', '0.00250000'], ['65493.93000000', '0.00009000'], ['65493.92000000', '0.00009000'], ['65493.84000000', '0.00018000'], ['65493.83000000', '0.07502000'], ['65493.59000000', '0.00018000']]	[['65500.34000000', '0.87207000'], ['65500.35000000', '0.00009000'], ['65500.81000000', '0.01368000'], ['65501.85000000', '0.01347000'], ['65502.85000000', '0.02000000'], ['65502.90000000', '0.05600000'], ['65504.08000000', '0.00031000'], ['65504.25000000', '0.02263000'], ['65504.70000000', '0.00009000'], ['65506.01000000', '0.07720000'], ['65506.55000000', '0.00008000'], ['65506.86000000', '0.00012000'], ['65506.90000000', '0.24750000'], ['65507.68000000', '0.02282000'], ['65507.90000000', '0.50451000'], ['65508.52000000', '0.06271000'], ['65509.77000000', '0.00009000'], ['65509.84000000', '0.00010000'], ['65510.20000000', '0.00008000'], ['65510.67000000', '0.00031000']]	\N	\N	2026-02-06 02:03:26.164853
18	ETHUSDT	1932.88	1932.89	0.009999999999990905	[['1932.88000000', '5.43830000'], ['1932.84000000', '0.00560000'], ['1932.83000000', '3.19860000'], ['1932.80000000', '0.00260000'], ['1932.79000000', '0.00270000'], ['1932.78000000', '0.00260000'], ['1932.75000000', '0.00520000'], ['1932.72000000', '0.01080000'], ['1932.70000000', '0.00260000'], ['1932.69000000', '0.00830000'], ['1932.68000000', '3.15000000'], ['1932.66000000', '0.00520000'], ['1932.63000000', '0.05670000'], ['1932.62000000', '0.00270000'], ['1932.60000000', '0.05990000'], ['1932.59000000', '0.06390000'], ['1932.57000000', '0.00840000'], ['1932.55000000', '0.00780000'], ['1932.50000000', '0.53110000'], ['1932.49000000', '0.75220000']]	[['1932.89000000', '6.95270000'], ['1932.90000000', '0.00540000'], ['1932.93000000', '0.00600000'], ['1932.98000000', '0.00280000'], ['1932.99000000', '0.00280000'], ['1933.00000000', '0.00540000'], ['1933.01000000', '0.00810000'], ['1933.02000000', '0.01130000'], ['1933.03000000', '0.00280000'], ['1933.04000000', '6.18560000'], ['1933.05000000', '5.18900000'], ['1933.06000000', '15.51060000'], ['1933.07000000', '0.00260000'], ['1933.10000000', '0.00260000'], ['1933.11000000', '7.29090000'], ['1933.12000000', '13.74290000'], ['1933.14000000', '0.00520000'], ['1933.15000000', '3.20200000'], ['1933.16000000', '8.80130000'], ['1933.17000000', '0.05170000']]	\N	\N	2026-02-06 02:03:26.758346
19	SOLUSDT	79.66	79.67	0.010000000000005116	[['79.66000000', '327.38100000'], ['79.65000000', '38.89600000'], ['79.64000000', '144.70000000'], ['79.63000000', '667.30300000'], ['79.62000000', '831.97000000'], ['79.61000000', '497.10900000'], ['79.60000000', '596.03700000'], ['79.59000000', '924.41100000'], ['79.58000000', '450.42900000'], ['79.57000000', '704.47800000'], ['79.56000000', '1227.50200000'], ['79.55000000', '748.71200000'], ['79.54000000', '111.24700000'], ['79.53000000', '285.60700000'], ['79.52000000', '450.37000000'], ['79.51000000', '288.44800000'], ['79.50000000', '732.24700000'], ['79.49000000', '586.94000000'], ['79.48000000', '107.51600000'], ['79.47000000', '80.05500000']]	[['79.67000000', '104.60600000'], ['79.68000000', '444.58600000'], ['79.69000000', '352.35400000'], ['79.70000000', '362.55800000'], ['79.71000000', '380.64800000'], ['79.72000000', '363.78300000'], ['79.73000000', '551.41300000'], ['79.74000000', '432.85900000'], ['79.75000000', '527.38400000'], ['79.76000000', '406.78200000'], ['79.77000000', '38.28600000'], ['79.78000000', '218.26300000'], ['79.79000000', '472.72400000'], ['79.80000000', '40.36000000'], ['79.81000000', '550.71900000'], ['79.82000000', '199.85600000'], ['79.83000000', '43.45300000'], ['79.84000000', '499.55400000'], ['79.85000000', '14.83900000'], ['79.86000000', '1.52200000']]	\N	\N	2026-02-06 02:03:27.353315
20	BNBUSDT	629.84	629.85	0.009999999999990905	[['629.84000000', '0.83300000'], ['629.83000000', '0.87000000'], ['629.82000000', '0.87000000'], ['629.81000000', '0.00900000'], ['629.80000000', '0.02600000'], ['629.79000000', '0.00900000'], ['629.78000000', '0.00900000'], ['629.77000000', '0.03800000'], ['629.76000000', '0.01000000'], ['629.75000000', '0.00900000'], ['629.74000000', '0.00900000'], ['629.73000000', '0.01700000'], ['629.72000000', '0.01700000'], ['629.71000000', '1.82900000'], ['629.70000000', '0.01800000'], ['629.68000000', '0.04000000'], ['629.66000000', '0.41700000'], ['629.65000000', '0.03800000'], ['629.64000000', '0.04500000'], ['629.63000000', '2.06700000']]	[['629.85000000', '5.26600000'], ['629.86000000', '0.87000000'], ['629.87000000', '0.87000000'], ['629.88000000', '0.86100000'], ['629.89000000', '0.86900000'], ['629.91000000', '0.00800000'], ['629.92000000', '0.02900000'], ['629.94000000', '0.01800000'], ['629.95000000', '1.11500000'], ['629.96000000', '0.73500000'], ['629.97000000', '1.81600000'], ['629.98000000', '0.01200000'], ['629.99000000', '0.01700000'], ['630.00000000', '0.03700000'], ['630.02000000', '0.01700000'], ['630.03000000', '0.80400000'], ['630.04000000', '0.04600000'], ['630.05000000', '1.80000000'], ['630.06000000', '0.01800000'], ['630.07000000', '0.02600000']]	\N	\N	2026-02-06 02:03:27.940469
21	BTCUSDT	64779.74	64779.75	0.010000000002037268	[['64779.74000000', '0.71159000'], ['64779.73000000', '0.00044000'], ['64779.72000000', '0.00027000'], ['64779.52000000', '0.00008000'], ['64778.19000000', '0.00334000'], ['64778.08000000', '0.00008000'], ['64777.99000000', '0.00018000'], ['64777.98000000', '0.19332000'], ['64777.97000000', '0.01423000'], ['64777.00000000', '0.00008000'], ['64776.97000000', '0.00018000'], ['64776.96000000', '0.01448000'], ['64776.85000000', '0.00018000'], ['64776.84000000', '0.51024000'], ['64776.56000000', '0.00009000'], ['64776.55000000', '0.00016000'], ['64776.14000000', '0.00010000'], ['64775.79000000', '0.02289000'], ['64775.36000000', '0.00250000'], ['64774.80000000', '0.00016000']]	[['64779.75000000', '1.30968000'], ['64780.20000000', '0.00266000'], ['64783.68000000', '0.00250000'], ['64783.85000000', '0.00008000'], ['64783.86000000', '0.00008000'], ['64785.44000000', '0.00250000'], ['64787.39000000', '0.00031000'], ['64787.50000000', '0.00008000'], ['64787.53000000', '0.00009000'], ['64787.58000000', '0.00012000'], ['64787.83000000', '0.00016000'], ['64787.84000000', '0.00250000'], ['64788.07000000', '0.01413000'], ['64788.69000000', '0.00008000'], ['64789.46000000', '0.00154000'], ['64789.66000000', '0.00250000'], ['64789.75000000', '0.00025000'], ['64790.22000000', '0.09865000'], ['64790.23000000', '0.15614000'], ['64790.72000000', '0.51022000']]	\N	\N	2026-02-06 02:13:31.376396
22	ETHUSDT	1913.54	1913.55	0.009999999999990905	[['1913.54000000', '4.07820000'], ['1913.53000000', '0.00280000'], ['1913.52000000', '0.00280000'], ['1913.50000000', '0.01350000'], ['1913.49000000', '0.00280000'], ['1913.47000000', '0.00550000'], ['1913.43000000', '0.00550000'], ['1913.42000000', '0.00840000'], ['1913.41000000', '0.06900000'], ['1913.40000000', '0.01270000'], ['1913.36000000', '0.00530000'], ['1913.32000000', '0.00830000'], ['1913.31000000', '1.99970000'], ['1913.30000000', '7.61370000'], ['1913.29000000', '3.15560000'], ['1913.28000000', '0.05000000'], ['1913.27000000', '0.01060000'], ['1913.22000000', '0.00590000'], ['1913.21000000', '0.01480000'], ['1913.20000000', '5.22570000']]	[['1913.55000000', '3.75910000'], ['1913.60000000', '0.00270000'], ['1913.65000000', '0.00560000'], ['1913.66000000', '0.75000000'], ['1913.68000000', '0.05950000'], ['1913.69000000', '1.85570000'], ['1913.70000000', '3.73870000'], ['1913.71000000', '1.00000000'], ['1913.72000000', '0.73340000'], ['1913.78000000', '2.31490000'], ['1913.79000000', '2.61200000'], ['1913.80000000', '13.22060000'], ['1913.81000000', '6.26890000'], ['1913.82000000', '0.00530000'], ['1913.83000000', '15.73280000'], ['1913.84000000', '0.00270000'], ['1913.85000000', '0.00320000'], ['1913.86000000', '0.01080000'], ['1913.88000000', '8.37570000'], ['1913.89000000', '0.07460000']]	\N	\N	2026-02-06 02:13:31.970863
23	SOLUSDT	78.16	78.17	0.010000000000005116	[['78.16000000', '0.47200000'], ['78.15000000', '40.63400000'], ['78.14000000', '28.13400000'], ['78.13000000', '96.32200000'], ['78.12000000', '32.28500000'], ['78.11000000', '667.87000000'], ['78.10000000', '345.88100000'], ['78.09000000', '371.07900000'], ['78.08000000', '368.50900000'], ['78.07000000', '562.22300000'], ['78.06000000', '377.45700000'], ['78.05000000', '200.43700000'], ['78.04000000', '542.11500000'], ['78.03000000', '30.68500000'], ['78.02000000', '462.76700000'], ['78.01000000', '156.09800000'], ['78.00000000', '127.36600000'], ['77.99000000', '547.87700000'], ['77.98000000', '554.80800000'], ['77.97000000', '155.56100000']]	[['78.17000000', '681.59700000'], ['78.18000000', '883.19800000'], ['78.19000000', '870.04400000'], ['78.20000000', '617.11700000'], ['78.21000000', '661.56700000'], ['78.22000000', '866.00000000'], ['78.23000000', '488.37200000'], ['78.24000000', '596.34600000'], ['78.25000000', '764.44300000'], ['78.26000000', '49.39500000'], ['78.27000000', '187.18900000'], ['78.28000000', '421.81900000'], ['78.29000000', '53.42700000'], ['78.30000000', '212.25300000'], ['78.31000000', '611.90300000'], ['78.32000000', '150.88400000'], ['78.33000000', '612.37400000'], ['78.34000000', '155.07100000'], ['78.35000000', '35.99400000'], ['78.36000000', '200.67600000']]	\N	\N	2026-02-06 02:13:32.570974
24	BNBUSDT	624.69	624.7	0.009999999999990905	[['624.69000000', '0.43000000'], ['624.68000000', '0.01800000'], ['624.67000000', '0.00900000'], ['624.66000000', '0.01800000'], ['624.65000000', '0.02600000'], ['624.64000000', '0.00900000'], ['624.63000000', '0.02100000'], ['624.62000000', '0.02600000'], ['624.61000000', '0.02200000'], ['624.60000000', '0.17800000'], ['624.59000000', '1.83500000'], ['624.56000000', '0.03600000'], ['624.55000000', '0.01300000'], ['624.54000000', '0.01900000'], ['624.53000000', '0.04300000'], ['624.52000000', '0.48800000'], ['624.51000000', '1.80900000'], ['624.50000000', '0.01700000'], ['624.49000000', '0.01300000'], ['624.48000000', '0.01900000']]	[['624.70000000', '7.04700000'], ['624.71000000', '0.53200000'], ['624.72000000', '1.70300000'], ['624.73000000', '1.17100000'], ['624.74000000', '9.16800000'], ['624.75000000', '1.18000000'], ['624.76000000', '1.17100000'], ['624.77000000', '2.00900000'], ['624.78000000', '0.02600000'], ['624.79000000', '1.17100000'], ['624.81000000', '2.63000000'], ['624.82000000', '0.02200000'], ['624.84000000', '2.63100000'], ['624.85000000', '10.48200000'], ['624.86000000', '9.02500000'], ['624.87000000', '0.02600000'], ['624.88000000', '1.30500000'], ['624.90000000', '1.05400000'], ['624.92000000', '1.82700000'], ['624.93000000', '0.02600000']]	\N	\N	2026-02-06 02:13:33.169745
25	BTCUSDT	64355.4	64355.41	0.010000000002037268	[['64355.40000000', '0.25739000'], ['64355.39000000', '0.00036000'], ['64355.38000000', '0.00045000'], ['64355.37000000', '0.05636000'], ['64355.36000000', '0.04826000'], ['64355.06000000', '0.00010000'], ['64354.66000000', '0.00018000'], ['64354.65000000', '0.01697000'], ['64354.60000000', '0.00018000'], ['64354.59000000', '0.09802000'], ['64354.41000000', '0.00008000'], ['64353.86000000', '0.00009000'], ['64353.85000000', '0.01740000'], ['64352.52000000', '0.00008000'], ['64351.92000000', '0.00031000'], ['64351.49000000', '0.00009000'], ['64351.48000000', '0.02370000'], ['64350.97000000', '0.02436000'], ['64350.82000000', '0.00300000'], ['64350.72000000', '0.00009000']]	[['64355.41000000', '0.79481000'], ['64355.42000000', '0.00009000'], ['64358.56000000', '0.00036000'], ['64359.32000000', '0.11950000'], ['64359.78000000', '0.00027000'], ['64359.79000000', '0.00031000'], ['64359.85000000', '0.00300000'], ['64360.98000000', '0.10425000'], ['64360.99000000', '0.05318000'], ['64361.00000000', '0.06358000'], ['64361.96000000', '0.00250000'], ['64362.00000000', '0.06358000'], ['64362.75000000', '0.00065000'], ['64362.80000000', '0.01705000'], ['64363.30000000', '0.03019000'], ['64364.28000000', '0.00009000'], ['64364.36000000', '0.00300000'], ['64364.55000000', '0.23341000'], ['64364.56000000', '0.10729000'], ['64364.57000000', '0.51342000']]	\N	\N	2026-02-06 02:23:39.046132
26	ETHUSDT	1895.38	1895.39	0.009999999999990905	[['1895.38000000', '5.19010000'], ['1895.36000000', '0.00270000'], ['1895.27000000', '6.34190000'], ['1895.26000000', '0.01690000'], ['1895.25000000', '1.00630000'], ['1895.23000000', '8.98100000'], ['1895.22000000', '13.73840000'], ['1895.20000000', '0.00280000'], ['1895.18000000', '0.00810000'], ['1895.17000000', '0.29780000'], ['1895.16000000', '0.00530000'], ['1895.15000000', '6.34190000'], ['1895.13000000', '0.00280000'], ['1895.11000000', '0.58160000'], ['1895.07000000', '3.15280000'], ['1895.06000000', '10.54140000'], ['1895.05000000', '6.34190000'], ['1895.04000000', '1.89000000'], ['1895.03000000', '1.85060000'], ['1895.01000000', '3.72230000']]	[['1895.39000000', '7.08000000'], ['1895.40000000', '0.00280000'], ['1895.44000000', '0.00280000'], ['1895.45000000', '0.00280000'], ['1895.46000000', '0.60090000'], ['1895.49000000', '0.00600000'], ['1895.50000000', '0.06550000'], ['1895.52000000', '0.28150000'], ['1895.53000000', '1.79970000'], ['1895.54000000', '4.13830000'], ['1895.55000000', '3.73870000'], ['1895.56000000', '0.00530000'], ['1895.58000000', '0.00320000'], ['1895.60000000', '0.00270000'], ['1895.61000000', '0.01620000'], ['1895.65000000', '0.00400000'], ['1895.67000000', '0.00850000'], ['1895.68000000', '0.00300000'], ['1895.72000000', '0.01070000'], ['1895.75000000', '3.26580000']]	\N	\N	2026-02-06 02:23:39.576214
27	SOLUSDT	77.05	77.06	0.010000000000005116	[['77.05000000', '28.86100000'], ['77.04000000', '226.77400000'], ['77.03000000', '528.27800000'], ['77.02000000', '2085.22700000'], ['77.01000000', '1013.35400000'], ['77.00000000', '1579.86700000'], ['76.99000000', '783.25400000'], ['76.98000000', '773.51000000'], ['76.97000000', '1710.30400000'], ['76.96000000', '1599.62100000'], ['76.95000000', '52.66600000'], ['76.94000000', '158.02800000'], ['76.93000000', '1639.49800000'], ['76.92000000', '210.83300000'], ['76.91000000', '54.60500000'], ['76.90000000', '701.62600000'], ['76.89000000', '642.72300000'], ['76.88000000', '213.14300000'], ['76.87000000', '1076.50500000'], ['76.86000000', '157.73900000']]	[['77.06000000', '154.76600000'], ['77.07000000', '926.59200000'], ['77.08000000', '749.65100000'], ['77.09000000', '824.67100000'], ['77.10000000', '802.67000000'], ['77.11000000', '848.29700000'], ['77.12000000', '1182.50500000'], ['77.13000000', '1685.21400000'], ['77.14000000', '568.67100000'], ['77.15000000', '2065.35500000'], ['77.16000000', '1119.27600000'], ['77.17000000', '217.85000000'], ['77.18000000', '373.17900000'], ['77.19000000', '1107.13600000'], ['77.20000000', '362.01000000'], ['77.21000000', '886.23100000'], ['77.22000000', '597.40900000'], ['77.23000000', '223.87800000'], ['77.24000000', '27.34500000'], ['77.25000000', '677.70000000']]	\N	\N	2026-02-06 02:23:40.096645
28	BNBUSDT	619.86	619.87	0.009999999999990905	[['619.86000000', '0.06800000'], ['619.85000000', '0.06100000'], ['619.84000000', '0.05600000'], ['619.83000000', '0.02200000'], ['619.82000000', '0.03500000'], ['619.81000000', '0.00900000'], ['619.80000000', '0.02800000'], ['619.79000000', '0.08900000'], ['619.78000000', '0.02600000'], ['619.77000000', '0.01300000'], ['619.76000000', '5.59700000'], ['619.75000000', '4.01200000'], ['619.74000000', '16.20700000'], ['619.73000000', '2.72900000'], ['619.72000000', '2.51000000'], ['619.71000000', '0.03000000'], ['619.70000000', '0.01700000'], ['619.68000000', '3.22100000'], ['619.67000000', '3.09000000'], ['619.66000000', '0.01300000']]	[['619.87000000', '6.01500000'], ['619.88000000', '1.78300000'], ['619.89000000', '1.18200000'], ['619.90000000', '5.05900000'], ['619.91000000', '1.17300000'], ['619.92000000', '1.17300000'], ['619.95000000', '0.02600000'], ['619.96000000', '2.01300000'], ['619.97000000', '1.80000000'], ['619.98000000', '0.03600000'], ['620.00000000', '0.01700000'], ['620.01000000', '0.61900000'], ['620.02000000', '0.64000000'], ['620.03000000', '0.62700000'], ['620.04000000', '0.01900000'], ['620.06000000', '0.78500000'], ['620.07000000', '0.00900000'], ['620.08000000', '0.03200000'], ['620.09000000', '0.01700000'], ['620.10000000', '1.83600000']]	\N	\N	2026-02-06 02:23:40.618981
29	BTCUSDT	64908.04	64908.05	0.010000000002037268	[['64908.04000000', '0.15533000'], ['64907.11000000', '0.00018000'], ['64907.09000000', '0.00027000'], ['64907.06000000', '0.00027000'], ['64907.00000000', '0.00008000'], ['64905.84000000', '0.00018000'], ['64905.44000000', '0.00018000'], ['64904.11000000', '0.00009000'], ['64901.90000000', '0.00031000'], ['64901.44000000', '0.00009000'], ['64901.14000000', '0.00311000'], ['64900.49000000', '0.08264000'], ['64900.48000000', '0.00024000'], ['64900.47000000', '0.00009000'], ['64900.42000000', '0.00018000'], ['64900.41000000', '0.00009000'], ['64899.30000000', '0.06973000'], ['64898.95000000', '0.00016000'], ['64898.31000000', '0.00154000'], ['64897.01000000', '0.03855000']]	[['64908.05000000', '0.55884000'], ['64908.06000000', '0.00009000'], ['64909.51000000', '0.00018000'], ['64909.52000000', '0.00277000'], ['64909.97000000', '0.00008000'], ['64911.45000000', '0.00012000'], ['64911.60000000', '0.00031000'], ['64912.32000000', '0.00277000'], ['64913.53000000', '0.00015000'], ['64913.83000000', '0.00017000'], ['64913.85000000', '0.05792000'], ['64915.13000000', '0.02156000'], ['64915.91000000', '0.02138000'], ['64916.15000000', '0.08837000'], ['64916.28000000', '0.00259000'], ['64916.50000000', '0.00010000'], ['64917.70000000', '0.06693000'], ['64917.71000000', '0.09494000'], ['64917.72000000', '0.00027000'], ['64917.85000000', '0.00016000']]	\N	\N	2026-02-06 02:33:49.437509
30	ETHUSDT	1922.84	1922.85	0.009999999999990905	[['1922.84000000', '5.55020000'], ['1922.76000000', '3.55620000'], ['1922.75000000', '0.31800000'], ['1922.74000000', '0.28590000'], ['1922.72000000', '0.01040000'], ['1922.70000000', '0.00280000'], ['1922.68000000', '0.00280000'], ['1922.67000000', '0.00870000'], ['1922.64000000', '0.00400000'], ['1922.63000000', '0.17420000'], ['1922.62000000', '0.00530000'], ['1922.60000000', '3.37100000'], ['1922.58000000', '0.00320000'], ['1922.55000000', '0.01080000'], ['1922.52000000', '0.00530000'], ['1922.51000000', '0.01870000'], ['1922.49000000', '0.00320000'], ['1922.46000000', '0.05510000'], ['1922.45000000', '0.00670000'], ['1922.44000000', '0.05730000']]	[['1922.85000000', '2.59920000'], ['1922.86000000', '15.66170000'], ['1922.87000000', '0.09450000'], ['1923.03000000', '0.00850000'], ['1923.04000000', '0.00530000'], ['1923.07000000', '1.25280000'], ['1923.11000000', '0.00530000'], ['1923.12000000', '0.00320000'], ['1923.14000000', '0.00400000'], ['1923.17000000', '0.00270000'], ['1923.18000000', '6.23650000'], ['1923.19000000', '0.00530000'], ['1923.21000000', '0.31650000'], ['1923.23000000', '0.01080000'], ['1923.26000000', '0.00530000'], ['1923.27000000', '39.52480000'], ['1923.28000000', '6.23650000'], ['1923.30000000', '0.00840000'], ['1923.33000000', '0.57140000'], ['1923.35000000', '5.20060000']]	\N	\N	2026-02-06 02:33:49.964289
31	SOLUSDT	77.94	77.95	0.010000000000005116	[['77.94000000', '257.24400000'], ['77.93000000', '116.17700000'], ['77.92000000', '184.73000000'], ['77.91000000', '785.14900000'], ['77.90000000', '658.47600000'], ['77.89000000', '3237.28100000'], ['77.88000000', '919.21700000'], ['77.87000000', '606.16600000'], ['77.86000000', '1669.01600000'], ['77.85000000', '620.35200000'], ['77.84000000', '801.64700000'], ['77.83000000', '1642.43800000'], ['77.82000000', '1745.21300000'], ['77.81000000', '27.36900000'], ['77.80000000', '1229.05200000'], ['77.79000000', '94.35600000'], ['77.78000000', '194.69000000'], ['77.77000000', '1117.79900000'], ['77.76000000', '1683.98000000'], ['77.75000000', '42.58700000']]	[['77.95000000', '22.57800000'], ['77.96000000', '1.20600000'], ['77.97000000', '567.81600000'], ['77.98000000', '832.34800000'], ['77.99000000', '983.31300000'], ['78.00000000', '1196.45700000'], ['78.01000000', '626.27900000'], ['78.02000000', '362.26700000'], ['78.03000000', '1251.60200000'], ['78.04000000', '397.45200000'], ['78.05000000', '116.38500000'], ['78.06000000', '202.39600000'], ['78.07000000', '477.32600000'], ['78.08000000', '1286.21200000'], ['78.09000000', '595.62100000'], ['78.10000000', '1677.69200000'], ['78.11000000', '2597.40600000'], ['78.12000000', '194.67200000'], ['78.13000000', '28.20100000'], ['78.14000000', '1061.23800000']]	\N	\N	2026-02-06 02:33:50.908714
32	BNBUSDT	625.78	625.79	0.009999999999990905	[['625.78000000', '9.62900000'], ['625.77000000', '3.29700000'], ['625.76000000', '2.02100000'], ['625.75000000', '2.10700000'], ['625.74000000', '5.49100000'], ['625.73000000', '2.11500000'], ['625.72000000', '2.10700000'], ['625.71000000', '0.00800000'], ['625.70000000', '4.80100000'], ['625.69000000', '1.52200000'], ['625.68000000', '17.52400000'], ['625.67000000', '0.01200000'], ['625.66000000', '0.02500000'], ['625.63000000', '0.01700000'], ['625.62000000', '0.03500000'], ['625.61000000', '5.80600000'], ['625.59000000', '7.99000000'], ['625.58000000', '0.75500000'], ['625.56000000', '0.02800000'], ['625.55000000', '0.02900000']]	[['625.79000000', '0.02700000'], ['625.80000000', '0.03400000'], ['625.81000000', '0.02600000'], ['625.82000000', '0.00900000'], ['625.83000000', '0.03400000'], ['625.84000000', '0.01800000'], ['625.85000000', '0.00900000'], ['625.86000000', '0.01700000'], ['625.87000000', '0.00900000'], ['625.88000000', '0.00900000'], ['625.89000000', '0.00800000'], ['625.90000000', '0.02600000'], ['625.91000000', '0.00800000'], ['625.92000000', '0.02500000'], ['625.95000000', '0.14400000'], ['625.96000000', '1.81700000'], ['625.98000000', '0.01800000'], ['625.99000000', '0.01700000'], ['626.00000000', '0.01700000'], ['626.01000000', '0.02000000']]	\N	\N	2026-02-06 02:33:51.434065
33	BTCUSDT	65323.87	65323.88	0.00999999999476131	[['65323.87000000', '0.78310000'], ['65323.86000000', '0.00009000'], ['65323.07000000', '0.02088000'], ['65323.00000000', '0.00027000'], ['65322.84000000', '0.00027000'], ['65321.90000000', '0.00008000'], ['65321.64000000', '0.00309000'], ['65321.41000000', '0.02285000'], ['65320.82000000', '0.05158000'], ['65320.81000000', '0.17047000'], ['65320.80000000', '0.00250000'], ['65320.55000000', '0.00031000'], ['65320.40000000', '0.00008000'], ['65319.29000000', '0.00018000'], ['65318.58000000', '0.00250000'], ['65318.44000000', '0.00010000'], ['65318.43000000', '0.00012000'], ['65318.37000000', '0.00018000'], ['65318.33000000', '0.00016000'], ['65317.48000000', '0.15994000']]	[['65323.88000000', '0.23668000'], ['65323.89000000', '0.00294000'], ['65324.05000000', '0.00008000'], ['65326.17000000', '0.00027000'], ['65326.19000000', '0.00009000'], ['65326.22000000', '0.00018000'], ['65326.23000000', '0.04161000'], ['65327.70000000', '0.00008000'], ['65330.81000000', '0.00300000'], ['65331.20000000', '0.00010000'], ['65331.35000000', '0.00008000'], ['65331.36000000', '0.00250000'], ['65331.78000000', '0.00031000'], ['65332.03000000', '0.00016000'], ['65333.30000000', '0.00012000'], ['65333.98000000', '0.00018000'], ['65333.99000000', '0.02808000'], ['65334.00000000', '0.06358000'], ['65334.40000000', '0.00250000'], ['65334.47000000', '0.00018000']]	\N	\N	2026-02-06 02:43:59.620493
34	ETHUSDT	1922.73	1922.74	0.009999999999990905	[['1922.73000000', '14.03320000'], ['1922.72000000', '20.77120000'], ['1922.70000000', '10.28120000'], ['1922.69000000', '0.00270000'], ['1922.68000000', '0.01080000'], ['1922.67000000', '5.05550000'], ['1922.66000000', '0.00270000'], ['1922.64000000', '5.05550000'], ['1922.63000000', '0.10810000'], ['1922.60000000', '0.00550000'], ['1922.58000000', '0.00280000'], ['1922.56000000', '0.05280000'], ['1922.55000000', '6.25240000'], ['1922.52000000', '0.00530000'], ['1922.51000000', '0.00530000'], ['1922.50000000', '0.00270000'], ['1922.46000000', '0.10000000'], ['1922.45000000', '0.00400000'], ['1922.43000000', '1.88550000'], ['1922.42000000', '6.25510000']]	[['1922.74000000', '0.05660000'], ['1922.76000000', '0.00280000'], ['1922.77000000', '0.00280000'], ['1922.80000000', '0.00550000'], ['1922.82000000', '0.00550000'], ['1922.83000000', '0.00630000'], ['1922.84000000', '0.00280000'], ['1922.85000000', '0.00630000'], ['1922.86000000', '0.00810000'], ['1922.87000000', '0.02000000'], ['1922.89000000', '0.01500000'], ['1922.90000000', '0.00540000'], ['1922.92000000', '0.00530000'], ['1922.94000000', '0.00560000'], ['1922.95000000', '0.00540000'], ['1922.96000000', '0.06560000'], ['1922.97000000', '2.91100000'], ['1922.99000000', '0.06330000'], ['1923.00000000', '0.02270000'], ['1923.01000000', '0.45290000']]	\N	\N	2026-02-06 02:44:00.571148
35	SOLUSDT	78.11	78.12	0.010000000000005116	[['78.11000000', '114.01400000'], ['78.10000000', '895.63800000'], ['78.09000000', '1204.03400000'], ['78.08000000', '1894.03500000'], ['78.07000000', '1307.34300000'], ['78.06000000', '662.35300000'], ['78.05000000', '1867.89900000'], ['78.04000000', '873.63600000'], ['78.03000000', '603.98700000'], ['78.02000000', '1133.24700000'], ['78.01000000', '559.42600000'], ['78.00000000', '89.06500000'], ['77.99000000', '658.67200000'], ['77.98000000', '132.10300000'], ['77.97000000', '177.29200000'], ['77.96000000', '577.67900000'], ['77.95000000', '757.61200000'], ['77.94000000', '257.96900000'], ['77.93000000', '569.95400000'], ['77.92000000', '222.68500000']]	[['78.12000000', '150.57300000'], ['78.13000000', '22.93700000'], ['78.14000000', '157.76100000'], ['78.15000000', '489.48400000'], ['78.16000000', '559.51800000'], ['78.17000000', '424.88100000'], ['78.18000000', '425.76700000'], ['78.19000000', '445.85900000'], ['78.20000000', '446.91600000'], ['78.21000000', '759.63800000'], ['78.22000000', '61.82900000'], ['78.23000000', '266.83900000'], ['78.24000000', '844.95200000'], ['78.25000000', '624.29700000'], ['78.26000000', '336.48300000'], ['78.27000000', '652.30900000'], ['78.28000000', '242.32000000'], ['78.29000000', '394.69300000'], ['78.30000000', '935.35900000'], ['78.31000000', '542.69900000']]	\N	\N	2026-02-06 02:44:01.097111
36	BNBUSDT	627.8	627.81	0.009999999999990905	[['627.80000000', '0.02600000'], ['627.79000000', '0.00900000'], ['627.78000000', '0.01700000'], ['627.77000000', '0.02100000'], ['627.76000000', '0.00900000'], ['627.75000000', '0.00900000'], ['627.74000000', '0.00900000'], ['627.73000000', '0.00900000'], ['627.72000000', '0.02900000'], ['627.71000000', '0.02900000'], ['627.69000000', '1.80000000'], ['627.68000000', '0.02700000'], ['627.66000000', '0.01800000'], ['627.65000000', '0.19700000'], ['627.64000000', '0.02700000'], ['627.63000000', '0.01700000'], ['627.62000000', '1.80000000'], ['627.60000000', '0.25900000'], ['627.59000000', '3.28600000'], ['627.58000000', '7.97300000']]	[['627.81000000', '16.20400000'], ['627.82000000', '2.51600000'], ['627.83000000', '9.10100000'], ['627.84000000', '5.62100000'], ['627.85000000', '2.51600000'], ['627.86000000', '2.50700000'], ['627.87000000', '1.90500000'], ['627.88000000', '1.89700000'], ['627.89000000', '0.85200000'], ['627.90000000', '2.32400000'], ['627.91000000', '0.01700000'], ['627.92000000', '1.85700000'], ['627.93000000', '0.02000000'], ['627.95000000', '5.93600000'], ['627.96000000', '0.01800000'], ['627.98000000', '0.01700000'], ['627.99000000', '0.02000000'], ['628.00000000', '0.61000000'], ['628.01000000', '4.67000000'], ['628.02000000', '0.83200000']]	\N	\N	2026-02-06 02:44:01.631158
37	BTCUSDT	65100.26	65100.27	0.00999999999476131	[['65100.26000000', '0.11871000'], ['65100.25000000', '0.00009000'], ['65099.64000000', '0.00010000'], ['65098.33000000', '0.00027000'], ['65097.75000000', '0.00008000'], ['65095.14000000', '0.00010000'], ['65094.65000000', '0.00016000'], ['65094.10000000', '0.00008000'], ['65094.00000000', '0.00009000'], ['65093.74000000', '0.00045000'], ['65093.40000000', '0.00009000'], ['65093.38000000', '0.00012000'], ['65092.48000000', '0.00009000'], ['65092.14000000', '0.00018000'], ['65092.13000000', '0.00016000'], ['65092.12000000', '0.00018000'], ['65091.83000000', '0.00031000'], ['65091.63000000', '0.00008000'], ['65091.50000000', '0.00018000'], ['65091.47000000', '0.00018000']]	[['65100.27000000', '2.39296000'], ['65100.28000000', '0.86630000'], ['65100.96000000', '0.00258000'], ['65101.40000000', '0.00541000'], ['65101.41000000', '2.06891000'], ['65103.00000000', '0.39793000'], ['65103.50000000', '0.00258000'], ['65104.70000000', '0.51600000'], ['65104.71000000', '0.00018000'], ['65104.72000000', '0.00018000'], ['65104.83000000', '0.20686000'], ['65104.84000000', '0.45136000'], ['65104.85000000', '0.18543000'], ['65104.86000000', '0.00008000'], ['65105.05000000', '0.00032000'], ['65105.20000000', '0.02348000'], ['65106.20000000', '0.00008000'], ['65107.15000000', '0.02295000'], ['65107.58000000', '0.00008000'], ['65107.68000000', '0.00250000']]	\N	\N	2026-02-06 02:46:12.249094
38	ETHUSDT	1914.96	1914.97	0.009999999999990905	[['1914.96000000', '7.85350000'], ['1914.95000000', '0.00270000'], ['1914.94000000', '0.00280000'], ['1914.93000000', '0.00600000'], ['1914.91000000', '0.00280000'], ['1914.90000000', '0.00550000'], ['1914.89000000', '0.00280000'], ['1914.88000000', '0.00550000'], ['1914.84000000', '0.00900000'], ['1914.83000000', '0.01340000'], ['1914.80000000', '0.00270000'], ['1914.79000000', '0.47030000'], ['1914.78000000', '0.01480000'], ['1914.75000000', '0.01010000'], ['1914.73000000', '0.00270000'], ['1914.72000000', '0.05840000'], ['1914.71000000', '6.25770000'], ['1914.70000000', '0.70660000'], ['1914.69000000', '3.15000000'], ['1914.68000000', '0.00270000']]	[['1914.97000000', '9.77680000'], ['1914.98000000', '0.00840000'], ['1914.99000000', '0.06890000'], ['1915.00000000', '0.00550000'], ['1915.01000000', '0.00900000'], ['1915.03000000', '0.00560000'], ['1915.04000000', '0.00280000'], ['1915.06000000', '0.00550000'], ['1915.09000000', '0.01110000'], ['1915.10000000', '4.50920000'], ['1915.11000000', '0.00830000'], ['1915.16000000', '0.00270000'], ['1915.18000000', '0.00280000'], ['1915.19000000', '3.15000000'], ['1915.20000000', '2.31460000'], ['1915.21000000', '2.71240000'], ['1915.23000000', '0.00530000'], ['1915.24000000', '0.00530000'], ['1915.25000000', '0.05220000'], ['1915.28000000', '0.00270000']]	\N	\N	2026-02-06 02:46:12.774881
39	SOLUSDT	77.53	77.54	0.010000000000005116	[['77.53000000', '560.44900000'], ['77.52000000', '403.66000000'], ['77.51000000', '595.83000000'], ['77.50000000', '661.83200000'], ['77.49000000', '1016.65100000'], ['77.48000000', '517.26500000'], ['77.47000000', '968.72700000'], ['77.46000000', '551.21600000'], ['77.45000000', '752.05500000'], ['77.44000000', '567.04700000'], ['77.43000000', '583.31000000'], ['77.42000000', '68.79300000'], ['77.41000000', '579.50800000'], ['77.40000000', '51.18200000'], ['77.39000000', '67.10800000'], ['77.38000000', '35.52600000'], ['77.37000000', '2591.64100000'], ['77.36000000', '625.94700000'], ['77.35000000', '221.23300000'], ['77.34000000', '125.46200000']]	[['77.54000000', '75.56800000'], ['77.55000000', '24.94000000'], ['77.56000000', '72.48200000'], ['77.57000000', '83.54300000'], ['77.58000000', '78.57000000'], ['77.59000000', '234.83900000'], ['77.60000000', '725.90700000'], ['77.61000000', '407.76000000'], ['77.62000000', '758.88500000'], ['77.63000000', '990.31700000'], ['77.64000000', '421.33400000'], ['77.65000000', '520.52900000'], ['77.66000000', '1045.64900000'], ['77.67000000', '653.40100000'], ['77.68000000', '235.25200000'], ['77.69000000', '573.12700000'], ['77.70000000', '148.46900000'], ['77.71000000', '237.71700000'], ['77.72000000', '883.53300000'], ['77.73000000', '514.26700000']]	\N	\N	2026-02-06 02:46:13.296943
40	BNBUSDT	625.16	625.17	0.009999999999990905	[['625.16000000', '1.61100000'], ['625.15000000', '1.62000000'], ['625.14000000', '2.22900000'], ['625.13000000', '0.00900000'], ['625.12000000', '1.62000000'], ['625.11000000', '1.62000000'], ['625.10000000', '1.63200000'], ['625.09000000', '1.63700000'], ['625.08000000', '1.63800000'], ['625.07000000', '1.61100000'], ['625.06000000', '4.61300000'], ['625.05000000', '3.33100000'], ['625.04000000', '0.63100000'], ['625.03000000', '0.01700000'], ['625.02000000', '0.01800000'], ['624.98000000', '3.86900000'], ['624.97000000', '0.01700000'], ['624.96000000', '14.51400000'], ['624.95000000', '4.47000000'], ['624.93000000', '17.13600000']]	[['625.17000000', '2.47600000'], ['625.18000000', '2.01800000'], ['625.19000000', '0.01800000'], ['625.20000000', '0.63600000'], ['625.21000000', '0.01800000'], ['625.22000000', '0.00900000'], ['625.23000000', '0.00800000'], ['625.24000000', '0.01000000'], ['625.25000000', '0.01700000'], ['625.26000000', '0.00800000'], ['625.27000000', '1.81200000'], ['625.28000000', '0.02700000'], ['625.29000000', '4.14800000'], ['625.30000000', '92.52800000'], ['625.31000000', '0.01700000'], ['625.32000000', '0.02800000'], ['625.33000000', '0.77500000'], ['625.34000000', '1.80000000'], ['625.35000000', '0.00800000'], ['625.36000000', '0.01700000']]	\N	\N	2026-02-06 02:46:13.822593
41	BTCUSDT	64747.85	64747.86	0.010000000002037268	[['64747.85000000', '1.87180000'], ['64747.77000000', '0.00018000'], ['64747.76000000', '0.00876000'], ['64747.73000000', '0.00010000'], ['64747.64000000', '0.00045000'], ['64747.63000000', '0.51048000'], ['64747.35000000', '0.00008000'], ['64746.23000000', '0.00021000'], ['64744.61000000', '0.00053000'], ['64743.70000000', '0.00008000'], ['64743.61000000', '0.00016000'], ['64743.31000000', '0.00300000'], ['64742.56000000', '0.00018000'], ['64742.24000000', '0.02000000'], ['64742.08000000', '0.00250000'], ['64742.07000000', '0.00008000'], ['64741.95000000', '0.00016000'], ['64741.57000000', '0.00008000'], ['64741.00000000', '0.00153000'], ['64740.61000000', '0.09839000']]	[['64747.86000000', '1.18615000'], ['64747.87000000', '0.00009000'], ['64748.01000000', '0.00027000'], ['64748.67000000', '0.00027000'], ['64748.92000000', '0.00008000'], ['64749.63000000', '0.00018000'], ['64749.64000000', '0.00927000'], ['64750.39000000', '0.01699000'], ['64750.40000000', '0.02177000'], ['64750.62000000', '0.00010000'], ['64750.84000000', '0.00008000'], ['64751.00000000', '0.00008000'], ['64751.11000000', '0.00018000'], ['64751.12000000', '0.02628000'], ['64751.68000000', '0.00250000'], ['64752.40000000', '0.00300000'], ['64752.45000000', '0.00250000'], ['64753.94000000', '0.70188000'], ['64753.95000000', '0.02279000'], ['64754.34000000', '0.24768000']]	\N	\N	2026-02-06 02:56:14.758577
42	ETHUSDT	1901.14	1901.15	0.009999999999990905	[['1901.14000000', '9.71110000'], ['1901.13000000', '0.00830000'], ['1901.12000000', '0.00560000'], ['1901.11000000', '5.28750000'], ['1901.10000000', '0.00270000'], ['1901.04000000', '0.00270000'], ['1901.03000000', '0.08980000'], ['1901.01000000', '0.00560000'], ['1901.00000000', '0.00270000'], ['1900.96000000', '0.05270000'], ['1900.92000000', '0.00800000'], ['1900.91000000', '1.60460000'], ['1900.90000000', '3.74950000'], ['1900.88000000', '0.00930000'], ['1900.86000000', '0.05260000'], ['1900.85000000', '0.06000000'], ['1900.84000000', '0.00270000'], ['1900.82000000', '2.05710000'], ['1900.81000000', '3.16980000'], ['1900.80000000', '8.43620000']]	[['1901.15000000', '3.19730000'], ['1901.16000000', '0.00840000'], ['1901.17000000', '0.00280000'], ['1901.20000000', '0.00550000'], ['1901.21000000', '0.00280000'], ['1901.22000000', '0.47950000'], ['1901.23000000', '0.01630000'], ['1901.25000000', '0.00280000'], ['1901.26000000', '0.01110000'], ['1901.27000000', '0.06290000'], ['1901.28000000', '0.01110000'], ['1901.29000000', '0.31640000'], ['1901.30000000', '0.00830000'], ['1901.31000000', '0.31750000'], ['1901.34000000', '0.00600000'], ['1901.35000000', '0.29880000'], ['1901.38000000', '0.00530000'], ['1901.40000000', '4.05170000'], ['1901.41000000', '7.87460000'], ['1901.42000000', '0.00670000']]	\N	\N	2026-02-06 02:56:15.226879
43	SOLUSDT	76.5	76.51	0.010000000000005116	[['76.50000000', '360.31300000'], ['76.49000000', '51.25300000'], ['76.48000000', '109.89000000'], ['76.47000000', '658.54000000'], ['76.46000000', '1206.10200000'], ['76.45000000', '1739.75700000'], ['76.44000000', '811.58900000'], ['76.43000000', '750.50000000'], ['76.42000000', '1868.83700000'], ['76.41000000', '882.51900000'], ['76.40000000', '1167.66700000'], ['76.39000000', '1208.16300000'], ['76.38000000', '109.43400000'], ['76.37000000', '162.82700000'], ['76.36000000', '115.68700000'], ['76.35000000', '718.62800000'], ['76.34000000', '572.55600000'], ['76.33000000', '307.79100000'], ['76.32000000', '193.03400000'], ['76.31000000', '366.93400000']]	[['76.51000000', '137.86600000'], ['76.52000000', '57.54400000'], ['76.53000000', '750.43200000'], ['76.54000000', '783.57100000'], ['76.55000000', '819.20300000'], ['76.56000000', '1084.82500000'], ['76.57000000', '1708.02900000'], ['76.58000000', '258.50800000'], ['76.59000000', '1046.82900000'], ['76.60000000', '1302.57100000'], ['76.61000000', '376.50800000'], ['76.62000000', '944.93300000'], ['76.63000000', '1304.63300000'], ['76.64000000', '200.53300000'], ['76.65000000', '269.25400000'], ['76.66000000', '744.84400000'], ['76.67000000', '37.37100000'], ['76.68000000', '329.78000000'], ['76.69000000', '1069.03000000'], ['76.70000000', '65.53200000']]	\N	\N	2026-02-06 02:56:15.688626
44	BNBUSDT	620.81	620.82	0.010000000000104592	[['620.81000000', '0.00900000'], ['620.80000000', '0.00900000'], ['620.79000000', '0.00900000'], ['620.78000000', '0.00900000'], ['620.77000000', '0.00900000'], ['620.76000000', '0.01800000'], ['620.75000000', '1.99500000'], ['620.74000000', '2.62200000'], ['620.73000000', '2.60500000'], ['620.72000000', '2.60900000'], ['620.71000000', '2.61300000'], ['620.70000000', '0.61900000'], ['620.69000000', '0.01200000'], ['620.68000000', '0.01700000'], ['620.66000000', '0.01300000'], ['620.65000000', '0.01700000'], ['620.64000000', '0.02900000'], ['620.62000000', '2.02600000'], ['620.61000000', '0.02000000'], ['620.60000000', '16.13000000']]	[['620.82000000', '5.57300000'], ['620.83000000', '0.02500000'], ['620.84000000', '0.02600000'], ['620.85000000', '0.01800000'], ['620.86000000', '0.43900000'], ['620.88000000', '0.01900000'], ['620.89000000', '1.81300000'], ['620.90000000', '0.01700000'], ['620.91000000', '0.00900000'], ['620.93000000', '1.29000000'], ['620.94000000', '0.01900000'], ['620.95000000', '4.86800000'], ['620.96000000', '2.00900000'], ['620.97000000', '0.01800000'], ['620.98000000', '5.80800000'], ['621.00000000', '0.03800000'], ['621.01000000', '6.02000000'], ['621.02000000', '11.95900000'], ['621.03000000', '2.99100000'], ['621.04000000', '0.01000000']]	\N	\N	2026-02-06 02:56:16.159767
45	BTCUSDT	64925.56	64925.57	0.010000000002037268	[['64925.56000000', '1.25706000'], ['64925.55000000', '0.00036000'], ['64925.33000000', '0.00018000'], ['64925.32000000', '0.02152000'], ['64923.03000000', '0.00018000'], ['64922.88000000', '0.00010000'], ['64922.73000000', '0.00008000'], ['64922.55000000', '0.00008000'], ['64922.05000000', '0.00018000'], ['64922.04000000', '0.00283000'], ['64921.79000000', '0.00018000'], ['64921.78000000', '0.16613000'], ['64921.77000000', '0.50900000'], ['64921.74000000', '0.00300000'], ['64921.37000000', '0.00008000'], ['64921.36000000', '0.00153000'], ['64921.11000000', '0.00008000'], ['64921.04000000', '0.00016000'], ['64920.96000000', '0.00258000'], ['64920.33000000', '0.00031000']]	[['64925.57000000', '2.99376000'], ['64925.58000000', '0.33125000'], ['64926.20000000', '0.00008000'], ['64926.43000000', '0.01629000'], ['64926.44000000', '0.02090000'], ['64927.08000000', '0.00018000'], ['64927.09000000', '0.02152000'], ['64927.59000000', '0.00018000'], ['64927.60000000', '0.02340000'], ['64927.73000000', '0.00009000'], ['64927.74000000', '0.02081000'], ['64927.83000000', '0.00018000'], ['64928.44000000', '0.00018000'], ['64929.09000000', '0.00009000'], ['64929.74000000', '0.00009000'], ['64929.85000000', '0.00008000'], ['64930.50000000', '0.00250000'], ['64930.84000000', '0.08942000'], ['64930.85000000', '0.25783000'], ['64930.86000000', '0.00016000']]	\N	\N	2026-02-06 03:06:17.446584
46	ETHUSDT	1907.32	1907.33	0.009999999999990905	[['1907.32000000', '16.28670000'], ['1907.31000000', '0.00280000'], ['1907.30000000', '0.00550000'], ['1907.29000000', '0.00280000'], ['1907.28000000', '0.00600000'], ['1907.27000000', '0.02450000'], ['1907.26000000', '0.00280000'], ['1907.25000000', '0.01360000'], ['1907.24000000', '0.00280000'], ['1907.23000000', '0.00280000'], ['1907.20000000', '0.00810000'], ['1907.19000000', '0.00880000'], ['1907.18000000', '0.06750000'], ['1907.17000000', '0.00530000'], ['1907.15000000', '0.00930000'], ['1907.12000000', '0.01470000'], ['1907.11000000', '0.94750000'], ['1907.10000000', '3.15430000'], ['1907.08000000', '0.00270000'], ['1907.06000000', '0.00530000']]	[['1907.33000000', '7.16840000'], ['1907.38000000', '0.01350000'], ['1907.40000000', '0.00270000'], ['1907.50000000', '0.00270000'], ['1907.53000000', '3.15000000'], ['1907.55000000', '0.00270000'], ['1907.56000000', '0.97990000'], ['1907.57000000', '0.00530000'], ['1907.58000000', '0.00270000'], ['1907.59000000', '1.00000000'], ['1907.60000000', '0.00270000'], ['1907.66000000', '0.00530000'], ['1907.67000000', '0.00530000'], ['1907.69000000', '0.00400000'], ['1907.70000000', '0.00540000'], ['1907.74000000', '0.00270000'], ['1907.75000000', '2.00000000'], ['1907.76000000', '3.15530000'], ['1907.77000000', '0.01080000'], ['1907.78000000', '0.00530000']]	\N	\N	2026-02-06 03:06:17.968449
47	SOLUSDT	76.85	76.86	0.010000000000005116	[['76.85000000', '137.13600000'], ['76.84000000', '542.23600000'], ['76.83000000', '895.29900000'], ['76.82000000', '540.47200000'], ['76.81000000', '787.19300000'], ['76.80000000', '625.30100000'], ['76.79000000', '115.79900000'], ['76.78000000', '237.80000000'], ['76.77000000', '349.63400000'], ['76.76000000', '611.53800000'], ['76.75000000', '323.00200000'], ['76.74000000', '695.41200000'], ['76.73000000', '432.89200000'], ['76.72000000', '128.18200000'], ['76.71000000', '519.46500000'], ['76.70000000', '77.71200000'], ['76.69000000', '217.58700000'], ['76.68000000', '186.60700000'], ['76.67000000', '695.04900000'], ['76.66000000', '533.38100000']]	[['76.86000000', '364.04100000'], ['76.87000000', '370.86200000'], ['76.88000000', '60.68800000'], ['76.89000000', '151.78000000'], ['76.90000000', '496.35500000'], ['76.91000000', '420.12600000'], ['76.92000000', '578.51600000'], ['76.93000000', '944.30100000'], ['76.94000000', '591.27300000'], ['76.95000000', '1059.29900000'], ['76.96000000', '984.17500000'], ['76.97000000', '556.22400000'], ['76.98000000', '546.27700000'], ['76.99000000', '722.49200000'], ['77.00000000', '119.71500000'], ['77.01000000', '311.20600000'], ['77.02000000', '800.62000000'], ['77.03000000', '732.35300000'], ['77.04000000', '260.16700000'], ['77.05000000', '352.04600000']]	\N	\N	2026-02-06 03:06:18.492578
48	BNBUSDT	622.6	622.61	0.009999999999990905	[['622.60000000', '1.81900000'], ['622.59000000', '0.00900000'], ['622.58000000', '0.02200000'], ['622.57000000', '0.00900000'], ['622.56000000', '0.03800000'], ['622.55000000', '1.81700000'], ['622.53000000', '2.44600000'], ['622.52000000', '0.03000000'], ['622.51000000', '0.24600000'], ['622.50000000', '0.09600000'], ['622.49000000', '0.01700000'], ['622.48000000', '0.03600000'], ['622.46000000', '0.01300000'], ['622.45000000', '1.83000000'], ['622.44000000', '7.99200000'], ['622.43000000', '16.00800000'], ['622.42000000', '8.22400000'], ['622.41000000', '28.74100000'], ['622.40000000', '97.15500000'], ['622.39000000', '4.16800000']]	[['622.61000000', '0.68700000'], ['622.62000000', '0.69000000'], ['622.65000000', '0.41500000'], ['622.66000000', '3.52300000'], ['622.67000000', '0.00900000'], ['622.68000000', '0.00900000'], ['622.69000000', '0.00900000'], ['622.71000000', '0.69900000'], ['622.72000000', '3.50400000'], ['622.74000000', '1.80900000'], ['622.75000000', '3.33100000'], ['622.76000000', '2.61000000'], ['622.77000000', '2.41900000'], ['622.79000000', '0.61000000'], ['622.80000000', '2.47300000'], ['622.81000000', '0.03100000'], ['622.82000000', '0.01700000'], ['622.83000000', '0.00900000'], ['622.85000000', '0.01700000'], ['622.86000000', '1.82200000']]	\N	\N	2026-02-06 03:06:19.018267
49	BTCUSDT	64560	64560.01	0.010000000002037268	[['64560.00000000', '0.00329000'], ['64559.99000000', '0.00009000'], ['64559.77000000', '0.00008000'], ['64559.16000000', '0.00008000'], ['64559.05000000', '0.00018000'], ['64559.04000000', '0.00335000'], ['64558.77000000', '0.00027000'], ['64558.67000000', '0.00009000'], ['64558.13000000', '0.00008000'], ['64557.55000000', '0.00008000'], ['64556.51000000', '0.00017000'], ['64556.15000000', '0.00082000'], ['64555.69000000', '0.00009000'], ['64555.66000000', '0.00008000'], ['64555.53000000', '0.00018000'], ['64555.52000000', '0.00308000'], ['64554.54000000', '0.00018000'], ['64554.53000000', '0.00026000'], ['64553.90000000', '0.00008000'], ['64553.89000000', '0.00018000']]	[['64560.01000000', '2.35715000'], ['64560.12000000', '0.53820000'], ['64560.13000000', '0.00017000'], ['64560.14000000', '0.24803000'], ['64560.24000000', '0.24795000'], ['64560.35000000', '0.00250000'], ['64561.20000000', '0.00008000'], ['64561.21000000', '0.06114000'], ['64561.58000000', '0.01674000'], ['64562.23000000', '0.01712000'], ['64563.06000000', '0.01722000'], ['64563.30000000', '0.00266000'], ['64563.70000000', '0.00018000'], ['64563.71000000', '0.00018000'], ['64564.00000000', '0.04778000'], ['64564.56000000', '0.00267000'], ['64564.57000000', '0.01075000'], ['64564.85000000', '0.00008000'], ['64564.93000000', '0.00031000'], ['64565.72000000', '0.00009000']]	\N	\N	2026-02-06 03:16:20.243681
50	ETHUSDT	1897.08	1897.09	0.009999999999990905	[['1897.08000000', '2.85070000'], ['1897.07000000', '0.00280000'], ['1897.06000000', '0.00550000'], ['1897.03000000', '0.00280000'], ['1897.02000000', '0.00600000'], ['1897.01000000', '0.00280000'], ['1897.00000000', '0.00550000'], ['1896.99000000', '0.00280000'], ['1896.98000000', '0.00280000'], ['1896.97000000', '0.01080000'], ['1896.96000000', '0.01070000'], ['1896.94000000', '0.00560000'], ['1896.93000000', '0.57920000'], ['1896.92000000', '0.00530000'], ['1896.90000000', '0.00830000'], ['1896.89000000', '0.59870000'], ['1896.88000000', '0.02270000'], ['1896.87000000', '0.00960000'], ['1896.86000000', '0.32830000'], ['1896.85000000', '0.00290000']]	[['1897.09000000', '16.04770000'], ['1897.10000000', '0.00550000'], ['1897.11000000', '0.00280000'], ['1897.12000000', '0.00280000'], ['1897.20000000', '0.00550000'], ['1897.26000000', '0.00280000'], ['1897.27000000', '7.38060000'], ['1897.29000000', '1.59880000'], ['1897.30000000', '0.00550000'], ['1897.31000000', '3.15280000'], ['1897.32000000', '1.00000000'], ['1897.33000000', '6.60570000'], ['1897.34000000', '13.73950000'], ['1897.35000000', '1.00400000'], ['1897.36000000', '0.00270000'], ['1897.37000000', '7.37780000'], ['1897.38000000', '0.06000000'], ['1897.40000000', '0.05540000'], ['1897.43000000', '2.66350000'], ['1897.44000000', '1.57040000']]	\N	\N	2026-02-06 03:16:20.69345
51	SOLUSDT	76.62	76.63	0.009999999999990905	[['76.62000000', '655.92500000'], ['76.61000000', '705.06500000'], ['76.60000000', '1218.51400000'], ['76.59000000', '2138.17600000'], ['76.58000000', '699.80300000'], ['76.57000000', '516.98900000'], ['76.56000000', '1571.70300000'], ['76.55000000', '288.00400000'], ['76.54000000', '509.76200000'], ['76.53000000', '1217.09600000'], ['76.52000000', '204.71100000'], ['76.51000000', '92.17500000'], ['76.50000000', '971.39800000'], ['76.49000000', '33.30300000'], ['76.48000000', '268.92000000'], ['76.47000000', '1117.67400000'], ['76.46000000', '196.28700000'], ['76.45000000', '245.16900000'], ['76.44000000', '196.55100000'], ['76.43000000', '521.61000000']]	[['76.63000000', '55.73500000'], ['76.64000000', '35.11900000'], ['76.65000000', '59.08800000'], ['76.66000000', '270.56600000'], ['76.67000000', '721.48100000'], ['76.68000000', '491.93700000'], ['76.69000000', '806.97600000'], ['76.70000000', '439.59700000'], ['76.71000000', '532.80400000'], ['76.72000000', '872.95800000'], ['76.73000000', '642.25100000'], ['76.74000000', '1043.24000000'], ['76.75000000', '823.19900000'], ['76.76000000', '72.19100000'], ['76.77000000', '342.75300000'], ['76.78000000', '634.20800000'], ['76.79000000', '235.64100000'], ['76.80000000', '798.60000000'], ['76.81000000', '195.89500000'], ['76.82000000', '285.45600000']]	\N	\N	2026-02-06 03:16:21.137994
52	BNBUSDT	618.61	618.62	0.009999999999990905	[['618.61000000', '4.28500000'], ['618.60000000', '0.00900000'], ['618.58000000', '0.00900000'], ['618.57000000', '0.02400000'], ['618.56000000', '4.86400000'], ['618.54000000', '1.83200000'], ['618.53000000', '0.01700000'], ['618.50000000', '0.01700000'], ['618.49000000', '0.81000000'], ['618.48000000', '2.62700000'], ['618.47000000', '1.81700000'], ['618.46000000', '0.00900000'], ['618.44000000', '1.48900000'], ['618.43000000', '4.85400000'], ['618.42000000', '0.04500000'], ['618.41000000', '0.01700000'], ['618.40000000', '7.98300000'], ['618.39000000', '5.32800000'], ['618.38000000', '7.05600000'], ['618.36000000', '0.05100000']]	[['618.62000000', '0.03800000'], ['618.63000000', '0.02700000'], ['618.64000000', '0.01800000'], ['618.65000000', '2.43000000'], ['618.66000000', '0.02700000'], ['618.67000000', '2.43000000'], ['618.68000000', '3.04000000'], ['618.69000000', '3.06600000'], ['618.70000000', '3.04000000'], ['618.71000000', '1.80900000'], ['618.72000000', '2.45300000'], ['618.73000000', '5.48100000'], ['618.74000000', '5.20700000'], ['618.75000000', '2.30700000'], ['618.76000000', '0.00900000'], ['618.77000000', '4.88000000'], ['618.78000000', '2.81300000'], ['618.80000000', '0.01000000'], ['618.81000000', '4.16000000'], ['618.82000000', '2.00000000']]	\N	\N	2026-02-06 03:16:21.585282
53	BTCUSDT	64564.55	64564.56	0.00999999999476131	[['64564.55000000', '0.71895000'], ['64564.54000000', '0.00009000'], ['64563.67000000', '0.00027000'], ['64563.66000000', '0.00027000'], ['64563.65000000', '0.00008000'], ['64563.19000000', '0.00027000'], ['64563.18000000', '0.01924000'], ['64563.01000000', '0.00008000'], ['64561.20000000', '0.00008000'], ['64560.89000000', '0.00018000'], ['64560.88000000', '0.51194000'], ['64559.15000000', '0.00793000'], ['64558.91000000', '0.00031000'], ['64558.68000000', '0.01695000'], ['64558.15000000', '0.01676000'], ['64558.10000000', '0.00018000'], ['64558.09000000', '0.24768000'], ['64558.01000000', '0.00300000'], ['64557.55000000', '0.00008000'], ['64557.50000000', '0.01717000']]	[['64564.56000000', '0.56790000'], ['64564.57000000', '0.00009000'], ['64564.85000000', '0.00008000'], ['64564.89000000', '0.00027000'], ['64565.04000000', '0.00027000'], ['64565.05000000', '0.00016000'], ['64565.31000000', '0.00018000'], ['64565.32000000', '0.02320000'], ['64565.33000000', '0.01710000'], ['64565.59000000', '0.00008000'], ['64565.60000000', '0.00010000'], ['64565.87000000', '0.00018000'], ['64565.88000000', '0.02352000'], ['64565.97000000', '0.00018000'], ['64565.98000000', '0.01745000'], ['64566.23000000', '0.00012000'], ['64567.07000000', '0.00008000'], ['64567.18000000', '0.00008000'], ['64567.44000000', '0.00266000'], ['64567.97000000', '0.00009000']]	\N	\N	2026-02-06 03:25:20.286636
54	ETHUSDT	1891.46	1891.47	0.009999999999990905	[['1891.46000000', '5.40570000'], ['1891.43000000', '0.00280000'], ['1891.41000000', '0.01080000'], ['1891.40000000', '0.00550000'], ['1891.38000000', '0.00270000'], ['1891.36000000', '0.00840000'], ['1891.35000000', '0.10550000'], ['1891.31000000', '0.00280000'], ['1891.30000000', '0.01110000'], ['1891.29000000', '1.84820000'], ['1891.26000000', '0.00550000'], ['1891.25000000', '0.01080000'], ['1891.24000000', '7.41260000'], ['1891.21000000', '0.00400000'], ['1891.20000000', '0.05840000'], ['1891.19000000', '0.00530000'], ['1891.18000000', '0.05280000'], ['1891.15000000', '3.03510000'], ['1891.13000000', '7.40720000'], ['1891.10000000', '0.00270000']]	[['1891.47000000', '2.24920000'], ['1891.50000000', '0.00550000'], ['1891.51000000', '0.00280000'], ['1891.53000000', '0.00280000'], ['1891.55000000', '0.00280000'], ['1891.57000000', '0.01350000'], ['1891.58000000', '0.00280000'], ['1891.60000000', '0.00550000'], ['1891.61000000', '0.00550000'], ['1891.62000000', '0.01160000'], ['1891.63000000', '0.25110000'], ['1891.64000000', '0.05590000'], ['1891.65000000', '0.01750000'], ['1891.66000000', '3.15000000'], ['1891.67000000', '0.00270000'], ['1891.68000000', '0.05270000'], ['1891.69000000', '0.00810000'], ['1891.70000000', '0.23170000'], ['1891.71000000', '0.00320000'], ['1891.74000000', '0.00270000']]	\N	\N	2026-02-06 03:25:20.803442
55	SOLUSDT	76.21	76.22	0.010000000000005116	[['76.21000000', '148.11600000'], ['76.20000000', '258.18500000'], ['76.19000000', '572.02700000'], ['76.18000000', '296.96700000'], ['76.17000000', '314.36000000'], ['76.16000000', '388.95500000'], ['76.15000000', '565.07400000'], ['76.14000000', '855.08300000'], ['76.13000000', '687.52600000'], ['76.12000000', '101.38900000'], ['76.11000000', '706.18000000'], ['76.10000000', '376.46400000'], ['76.09000000', '41.78900000'], ['76.08000000', '253.24500000'], ['76.07000000', '1217.50400000'], ['76.06000000', '166.45900000'], ['76.05000000', '187.06800000'], ['76.04000000', '898.78700000'], ['76.03000000', '232.86400000'], ['76.02000000', '165.49200000']]	[['76.22000000', '356.16900000'], ['76.23000000', '181.88400000'], ['76.24000000', '302.99700000'], ['76.25000000', '437.28800000'], ['76.26000000', '491.27700000'], ['76.27000000', '464.72500000'], ['76.28000000', '446.59900000'], ['76.29000000', '331.92400000'], ['76.30000000', '795.25100000'], ['76.31000000', '240.82700000'], ['76.32000000', '246.38900000'], ['76.33000000', '841.72500000'], ['76.34000000', '231.70100000'], ['76.35000000', '769.76800000'], ['76.36000000', '784.05300000'], ['76.37000000', '218.19400000'], ['76.38000000', '412.75300000'], ['76.39000000', '1047.27700000'], ['76.40000000', '27.48400000'], ['76.41000000', '229.68500000']]	\N	\N	2026-02-06 03:25:21.317246
56	BNBUSDT	618.41	618.42	0.009999999999990905	[['618.41000000', '5.86600000'], ['618.40000000', '0.06600000'], ['618.39000000', '5.99800000'], ['618.38000000', '5.62900000'], ['618.37000000', '2.91800000'], ['618.36000000', '3.71200000'], ['618.35000000', '3.96600000'], ['618.34000000', '9.65300000'], ['618.33000000', '2.99500000'], ['618.32000000', '1.80400000'], ['618.31000000', '2.97900000'], ['618.30000000', '0.68300000'], ['618.29000000', '1.57200000'], ['618.28000000', '0.66700000'], ['618.27000000', '2.49100000'], ['618.26000000', '0.01300000'], ['618.24000000', '0.01900000'], ['618.23000000', '0.01700000'], ['618.21000000', '9.68600000'], ['618.20000000', '5.71200000']]	[['618.42000000', '2.33600000'], ['618.43000000', '0.03100000'], ['618.44000000', '2.29900000'], ['618.45000000', '0.02700000'], ['618.46000000', '0.00900000'], ['618.47000000', '0.00900000'], ['618.48000000', '0.03200000'], ['618.49000000', '0.00900000'], ['618.50000000', '0.02600000'], ['618.51000000', '0.07100000'], ['618.52000000', '1.89500000'], ['618.54000000', '0.04100000'], ['618.55000000', '0.01700000'], ['618.56000000', '4.85500000'], ['618.57000000', '0.81700000'], ['618.58000000', '0.75700000'], ['618.60000000', '3.27600000'], ['618.61000000', '2.54500000'], ['618.63000000', '4.99500000'], ['618.64000000', '7.86200000']]	\N	\N	2026-02-06 03:25:21.844167
57	BTCUSDT	64834.29	64834.3	0.010000000002037268	[['64834.29000000', '0.75300000'], ['64834.28000000', '0.00009000'], ['64834.13000000', '0.00008000'], ['64833.98000000', '0.00043000'], ['64833.97000000', '0.00027000'], ['64833.61000000', '0.00018000'], ['64833.60000000', '0.00259000'], ['64833.59000000', '0.00018000'], ['64833.58000000', '0.01430000'], ['64833.56000000', '0.00010000'], ['64833.32000000', '0.50961000'], ['64833.29000000', '0.00008000'], ['64833.22000000', '0.00018000'], ['64833.21000000', '0.00250000'], ['64832.94000000', '0.00018000'], ['64832.93000000', '0.01419000'], ['64832.29000000', '0.00009000'], ['64832.28000000', '0.01400000'], ['64831.46000000', '0.00560000'], ['64831.30000000', '0.00008000']]	[['64834.30000000', '1.77178000'], ['64834.60000000', '0.00035000'], ['64834.61000000', '0.07393000'], ['64834.95000000', '0.00008000'], ['64837.36000000', '0.00016000'], ['64838.60000000', '0.00008000'], ['64838.67000000', '0.00031000'], ['64840.74000000', '0.00018000'], ['64840.75000000', '0.02262000'], ['64840.76000000', '0.07409000'], ['64840.77000000', '0.24767000'], ['64841.67000000', '0.00267000'], ['64841.68000000', '0.00034000'], ['64841.92000000', '0.00258000'], ['64842.25000000', '0.00008000'], ['64843.20000000', '0.02055000'], ['64843.21000000', '0.00017000'], ['64843.58000000', '0.00012000'], ['64843.68000000', '0.04016000'], ['64843.85000000', '0.00017000']]	\N	\N	2026-02-06 03:35:23.261516
58	ETHUSDT	1902.38	1902.39	0.009999999999990905	[['1902.38000000', '0.04340000'], ['1902.37000000', '0.00280000'], ['1902.34000000', '0.00280000'], ['1902.33000000', '0.00280000'], ['1902.31000000', '0.01110000'], ['1902.30000000', '0.08260000'], ['1902.29000000', '0.01300000'], ['1902.28000000', '0.00270000'], ['1902.25000000', '0.00280000'], ['1902.24000000', '0.00580000'], ['1902.21000000', '0.01090000'], ['1902.20000000', '0.93270000'], ['1902.18000000', '0.00290000'], ['1902.17000000', '0.55680000'], ['1902.16000000', '0.00800000'], ['1902.15000000', '0.00320000'], ['1902.13000000', '0.53610000'], ['1902.12000000', '0.00270000'], ['1902.10000000', '0.00670000'], ['1902.09000000', '0.00530000']]	[['1902.39000000', '18.02210000'], ['1902.40000000', '1.58460000'], ['1902.41000000', '0.54060000'], ['1902.42000000', '3.15000000'], ['1902.45000000', '0.55420000'], ['1902.48000000', '3.39910000'], ['1902.49000000', '0.61830000'], ['1902.50000000', '0.00550000'], ['1902.51000000', '3.33120000'], ['1902.52000000', '2.12590000'], ['1902.53000000', '0.53990000'], ['1902.55000000', '0.00280000'], ['1902.56000000', '7.41290000'], ['1902.57000000', '3.23810000'], ['1902.58000000', '0.00280000'], ['1902.60000000', '3.62050000'], ['1902.61000000', '0.00530000'], ['1902.66000000', '1.85760000'], ['1902.67000000', '2.60710000'], ['1902.70000000', '7.31250000']]	\N	\N	2026-02-06 03:35:23.768478
59	SOLUSDT	76.85	76.86	0.010000000000005116	[['76.85000000', '81.79900000'], ['76.84000000', '271.36200000'], ['76.83000000', '268.56500000'], ['76.82000000', '309.71100000'], ['76.81000000', '410.76900000'], ['76.80000000', '799.83300000'], ['76.79000000', '788.59000000'], ['76.78000000', '109.38400000'], ['76.77000000', '64.41900000'], ['76.76000000', '285.60700000'], ['76.75000000', '896.84900000'], ['76.74000000', '256.12800000'], ['76.73000000', '531.35000000'], ['76.72000000', '776.34900000'], ['76.71000000', '27.19700000'], ['76.70000000', '211.05200000'], ['76.69000000', '860.43300000'], ['76.68000000', '197.61600000'], ['76.67000000', '547.25200000'], ['76.66000000', '812.88800000']]	[['76.86000000', '340.93700000'], ['76.87000000', '82.53000000'], ['76.88000000', '119.34000000'], ['76.89000000', '398.71200000'], ['76.90000000', '679.75800000'], ['76.91000000', '322.91900000'], ['76.92000000', '613.45400000'], ['76.93000000', '1076.00600000'], ['76.94000000', '459.99800000'], ['76.95000000', '559.03700000'], ['76.96000000', '973.98600000'], ['76.97000000', '327.53200000'], ['76.98000000', '411.25600000'], ['76.99000000', '789.64500000'], ['77.00000000', '326.68300000'], ['77.01000000', '632.30800000'], ['77.02000000', '197.80000000'], ['77.03000000', '405.18400000'], ['77.04000000', '847.83400000'], ['77.05000000', '219.12100000']]	\N	\N	2026-02-06 03:35:24.270697
60	BNBUSDT	620.11	620.12	0.009999999999990905	[['620.11000000', '0.02500000'], ['620.10000000', '0.05100000'], ['620.09000000', '0.02600000'], ['620.08000000', '0.01800000'], ['620.07000000', '0.02600000'], ['620.06000000', '0.02200000'], ['620.05000000', '0.00900000'], ['620.04000000', '0.02800000'], ['620.03000000', '4.85300000'], ['620.02000000', '0.00900000'], ['620.01000000', '0.04100000'], ['620.00000000', '0.04900000'], ['619.99000000', '0.14300000'], ['619.98000000', '0.01900000'], ['619.97000000', '0.01300000'], ['619.96000000', '4.04600000'], ['619.95000000', '0.00900000'], ['619.94000000', '1.81300000'], ['619.93000000', '0.06500000'], ['619.92000000', '0.01900000']]	[['620.12000000', '17.41000000'], ['620.13000000', '6.70700000'], ['620.14000000', '7.23300000'], ['620.15000000', '5.37800000'], ['620.16000000', '0.01800000'], ['620.19000000', '0.00900000'], ['620.20000000', '4.64200000'], ['620.21000000', '7.77800000'], ['620.22000000', '5.34900000'], ['620.23000000', '0.45000000'], ['620.24000000', '1.44900000'], ['620.25000000', '4.85400000'], ['620.26000000', '0.01700000'], ['620.28000000', '0.85400000'], ['620.29000000', '4.04400000'], ['620.30000000', '1.35200000'], ['620.31000000', '3.90900000'], ['620.32000000', '0.02700000'], ['620.33000000', '1.80000000'], ['620.34000000', '0.03200000']]	\N	\N	2026-02-06 03:35:24.765631
61	BTCUSDT	64490	64490.01	0.010000000002037268	[['64490.00000000', '0.05224000'], ['64489.99000000', '0.00054000'], ['64489.98000000', '1.00036000'], ['64489.80000000', '0.00009000'], ['64489.04000000', '0.00008000'], ['64488.82000000', '0.00012000'], ['64488.51000000', '0.00008000'], ['64488.20000000', '0.00008000'], ['64487.52000000', '0.00009000'], ['64486.97000000', '0.00008000'], ['64486.34000000', '0.00018000'], ['64486.33000000', '0.17532000'], ['64486.32000000', '0.01595000'], ['64486.20000000', '0.00008000'], ['64485.89000000', '0.00016000'], ['64485.71000000', '0.00387000'], ['64485.24000000', '0.00009000'], ['64485.04000000', '0.00621000'], ['64485.03000000', '0.45638000'], ['64485.00000000', '0.00029000']]	[['64490.01000000', '3.13168000'], ['64490.02000000', '0.00009000'], ['64490.58000000', '0.00276000'], ['64490.67000000', '0.01758000'], ['64490.68000000', '0.01759000'], ['64490.80000000', '0.02312000'], ['64490.85000000', '0.00259000'], ['64491.03000000', '0.00271000'], ['64491.45000000', '0.00008000'], ['64491.74000000', '0.00008000'], ['64491.85000000', '0.00008000'], ['64491.96000000', '0.01714000'], ['64492.20000000', '0.00250000'], ['64492.24000000', '0.00008000'], ['64492.40000000', '0.00266000'], ['64492.61000000', '0.01730000'], ['64492.98000000', '0.05792000'], ['64493.49000000', '0.00018000'], ['64493.50000000', '0.03503000'], ['64493.51000000', '0.00043000']]	\N	\N	2026-02-06 03:45:32.264664
62	ETHUSDT	1890.01	1890.02	0.009999999999990905	[['1890.01000000', '10.74250000'], ['1890.00000000', '0.01930000'], ['1889.99000000', '0.00280000'], ['1889.96000000', '0.00280000'], ['1889.94000000', '0.00980000'], ['1889.92000000', '0.00280000'], ['1889.91000000', '0.01410000'], ['1889.90000000', '0.00550000'], ['1889.88000000', '0.00580000'], ['1889.87000000', '0.00530000'], ['1889.85000000', '0.00540000'], ['1889.84000000', '0.00570000'], ['1889.82000000', '0.01180000'], ['1889.81000000', '0.49550000'], ['1889.80000000', '0.00270000'], ['1889.79000000', '0.00810000'], ['1889.78000000', '0.00830000'], ['1889.77000000', '0.06270000'], ['1889.76000000', '0.00300000'], ['1889.75000000', '0.00960000']]	[['1890.02000000', '32.35390000'], ['1890.04000000', '14.40770000'], ['1890.05000000', '3.87220000'], ['1890.08000000', '3.20630000'], ['1890.09000000', '0.54660000'], ['1890.10000000', '2.41970000'], ['1890.13000000', '2.67850000'], ['1890.14000000', '0.00280000'], ['1890.15000000', '2.31700000'], ['1890.16000000', '0.05280000'], ['1890.17000000', '0.54620000'], ['1890.18000000', '2.95940000'], ['1890.19000000', '2.14000000'], ['1890.20000000', '0.00270000'], ['1890.21000000', '1.00010000'], ['1890.23000000', '0.00760000'], ['1890.24000000', '0.05000000'], ['1890.25000000', '0.00530000'], ['1890.28000000', '0.00540000'], ['1890.30000000', '0.00270000']]	\N	\N	2026-02-06 03:45:33.223838
63	SOLUSDT	76.23	76.24	0.009999999999990905	[['76.23000000', '85.39000000'], ['76.22000000', '112.44000000'], ['76.21000000', '451.80800000'], ['76.20000000', '400.06000000'], ['76.19000000', '496.43200000'], ['76.18000000', '468.50400000'], ['76.17000000', '771.71500000'], ['76.16000000', '719.72900000'], ['76.15000000', '294.42100000'], ['76.14000000', '899.21900000'], ['76.13000000', '833.00000000'], ['76.12000000', '455.93900000'], ['76.11000000', '300.00700000'], ['76.10000000', '895.69100000'], ['76.09000000', '164.94900000'], ['76.08000000', '661.20500000'], ['76.07000000', '718.17200000'], ['76.06000000', '28.66200000'], ['76.05000000', '237.09300000'], ['76.04000000', '816.87900000']]	[['76.24000000', '178.24400000'], ['76.25000000', '266.79900000'], ['76.26000000', '363.47900000'], ['76.27000000', '345.68900000'], ['76.28000000', '763.91200000'], ['76.29000000', '1037.89000000'], ['76.30000000', '1123.01100000'], ['76.31000000', '375.28700000'], ['76.32000000', '707.59600000'], ['76.33000000', '990.34700000'], ['76.34000000', '453.48400000'], ['76.35000000', '794.30400000'], ['76.36000000', '832.54300000'], ['76.37000000', '41.27600000'], ['76.38000000', '247.44800000'], ['76.39000000', '278.55500000'], ['76.40000000', '1102.78100000'], ['76.41000000', '710.76300000'], ['76.42000000', '461.63800000'], ['76.43000000', '95.63100000']]	\N	\N	2026-02-06 03:45:33.755218
64	BNBUSDT	615.74	615.75	0.009999999999990905	[['615.74000000', '14.75700000'], ['615.73000000', '8.62200000'], ['615.72000000', '15.31800000'], ['615.68000000', '0.01300000'], ['615.66000000', '0.02800000'], ['615.65000000', '2.52400000'], ['615.64000000', '2.70700000'], ['615.63000000', '0.69800000'], ['615.62000000', '3.20100000'], ['615.61000000', '1.36500000'], ['615.60000000', '0.01900000'], ['615.59000000', '0.69800000'], ['615.58000000', '3.78000000'], ['615.57000000', '0.01700000'], ['615.56000000', '1.03300000'], ['615.55000000', '9.77300000'], ['615.54000000', '0.01900000'], ['615.53000000', '0.01700000'], ['615.52000000', '0.02700000'], ['615.51000000', '0.63400000']]	[['615.75000000', '0.04500000'], ['615.76000000', '0.01800000'], ['615.77000000', '0.01800000'], ['615.78000000', '0.72500000'], ['615.79000000', '0.01800000'], ['615.80000000', '0.72400000'], ['615.81000000', '0.03500000'], ['615.82000000', '0.02200000'], ['615.83000000', '4.86300000'], ['615.84000000', '3.66500000'], ['615.85000000', '0.01700000'], ['615.86000000', '0.00900000'], ['615.87000000', '0.23200000'], ['615.88000000', '2.70900000'], ['615.90000000', '1.62900000'], ['615.91000000', '91.09700000'], ['615.92000000', '19.96600000'], ['615.93000000', '0.01800000'], ['615.94000000', '0.01300000'], ['615.95000000', '1.77700000']]	\N	\N	2026-02-06 03:45:34.700794
65	BTCUSDT	64073.17	64073.18	0.010000000002037268	[['64073.17000000', '2.14259000'], ['64073.16000000', '0.00009000'], ['64072.54000000', '1.03182000'], ['64072.53000000', '0.51566000'], ['64072.52000000', '0.24279000'], ['64072.10000000', '0.00008000'], ['64071.94000000', '0.02335000'], ['64071.73000000', '0.00027000'], ['64071.72000000', '2.10536000'], ['64071.71000000', '0.00027000'], ['64071.70000000', '0.00035000'], ['64071.16000000', '0.00008000'], ['64071.04000000', '0.00250000'], ['64070.79000000', '0.00250000'], ['64070.73000000', '0.00031000'], ['64070.03000000', '0.01400000'], ['64069.94000000', '0.00008000'], ['64069.29000000', '0.01407000'], ['64068.93000000', '0.00008000'], ['64068.64000000', '0.01417000']]	[['64073.18000000', '0.30500000'], ['64073.19000000', '0.00009000'], ['64073.83000000', '0.00018000'], ['64073.99000000', '0.00012000'], ['64074.35000000', '0.00018000'], ['64074.36000000', '0.00008000'], ['64075.75000000', '0.00008000'], ['64077.77000000', '0.00009000'], ['64078.02000000', '0.00008000'], ['64078.56000000', '0.00026000'], ['64078.66000000', '0.00018000'], ['64078.67000000', '0.01423000'], ['64078.91000000', '0.00018000'], ['64079.00000000', '0.00018000'], ['64079.01000000', '0.00258000'], ['64079.06000000', '0.00016000'], ['64079.31000000', '0.00018000'], ['64079.32000000', '0.01424000'], ['64079.33000000', '0.00164000'], ['64079.40000000', '0.00258000']]	\N	\N	2026-02-06 03:55:38.095651
66	ETHUSDT	1888.63	1888.64	0.009999999999990905	[['1888.63000000', '3.14930000'], ['1888.60000000', '0.00550000'], ['1888.59000000', '0.00280000'], ['1888.58000000', '0.00280000'], ['1888.55000000', '0.00280000'], ['1888.54000000', '0.00280000'], ['1888.53000000', '0.00280000'], ['1888.52000000', '0.00280000'], ['1888.51000000', '0.00280000'], ['1888.50000000', '0.00550000'], ['1888.47000000', '0.00560000'], ['1888.46000000', '5.30430000'], ['1888.44000000', '0.01900000'], ['1888.43000000', '3.08220000'], ['1888.42000000', '0.01080000'], ['1888.40000000', '0.00270000'], ['1888.39000000', '0.00960000'], ['1888.38000000', '0.00560000'], ['1888.37000000', '0.48020000'], ['1888.36000000', '0.00810000']]	[['1888.64000000', '9.10150000'], ['1888.65000000', '0.00280000'], ['1888.66000000', '0.37700000'], ['1888.67000000', '0.00280000'], ['1888.68000000', '0.44000000'], ['1888.69000000', '0.00280000'], ['1888.70000000', '0.38900000'], ['1888.71000000', '0.00680000'], ['1888.72000000', '0.37350000'], ['1888.73000000', '0.49150000'], ['1888.74000000', '0.39000000'], ['1888.75000000', '0.00530000'], ['1888.76000000', '1.30390000'], ['1888.77000000', '0.47230000'], ['1888.78000000', '0.37070000'], ['1888.79000000', '1.00000000'], ['1888.80000000', '0.42940000'], ['1888.81000000', '0.48310000'], ['1888.82000000', '0.37070000'], ['1888.83000000', '0.62970000']]	\N	\N	2026-02-06 03:55:38.678099
67	SOLUSDT	76.43	76.44	0.009999999999990905	[['76.43000000', '3.30900000'], ['76.42000000', '29.10600000'], ['76.41000000', '18.59800000'], ['76.40000000', '259.20600000'], ['76.39000000', '1577.01300000'], ['76.38000000', '447.67000000'], ['76.37000000', '262.62000000'], ['76.36000000', '903.46900000'], ['76.35000000', '249.93000000'], ['76.34000000', '14.21800000'], ['76.33000000', '1459.82400000'], ['76.32000000', '100.05900000'], ['76.31000000', '186.90800000'], ['76.30000000', '660.36300000'], ['76.29000000', '223.67700000'], ['76.28000000', '5.07400000'], ['76.27000000', '1221.40600000'], ['76.26000000', '181.69600000'], ['76.25000000', '132.80500000'], ['76.24000000', '696.32900000']]	[['76.44000000', '259.77700000'], ['76.45000000', '57.81500000'], ['76.46000000', '119.56300000'], ['76.47000000', '394.97700000'], ['76.48000000', '391.01900000'], ['76.49000000', '584.20700000'], ['76.50000000', '1181.06800000'], ['76.51000000', '1095.48900000'], ['76.52000000', '410.87000000'], ['76.53000000', '547.68800000'], ['76.54000000', '717.67700000'], ['76.55000000', '187.95200000'], ['76.56000000', '333.80600000'], ['76.57000000', '883.49200000'], ['76.58000000', '839.20300000'], ['76.59000000', '427.16100000'], ['76.60000000', '110.05100000'], ['76.61000000', '175.50000000'], ['76.62000000', '538.62100000'], ['76.63000000', '1008.85000000']]	\N	\N	2026-02-06 03:55:39.265988
68	BNBUSDT	614.77	614.78	0.009999999999990905	[['614.77000000', '0.04500000'], ['614.76000000', '0.03700000'], ['614.75000000', '0.01800000'], ['614.74000000', '0.02700000'], ['614.73000000', '2.02700000'], ['614.72000000', '1.17500000'], ['614.71000000', '0.00900000'], ['614.70000000', '0.05400000'], ['614.69000000', '0.02600000'], ['614.68000000', '0.01700000'], ['614.67000000', '0.93300000'], ['614.66000000', '1.80000000'], ['614.65000000', '0.01700000'], ['614.64000000', '4.92800000'], ['614.62000000', '0.57500000'], ['614.61000000', '8.72600000'], ['614.60000000', '2.01000000'], ['614.59000000', '6.58800000'], ['614.58000000', '0.02300000'], ['614.57000000', '0.01700000']]	[['614.78000000', '11.66600000'], ['614.79000000', '0.01800000'], ['614.80000000', '2.94200000'], ['614.82000000', '0.00900000'], ['614.83000000', '5.66400000'], ['614.84000000', '2.93200000'], ['614.85000000', '6.70500000'], ['614.86000000', '2.96200000'], ['614.87000000', '3.63000000'], ['614.88000000', '7.82500000'], ['614.89000000', '0.71500000'], ['614.90000000', '0.69800000'], ['614.91000000', '0.02600000'], ['614.92000000', '0.01300000'], ['614.93000000', '0.81400000'], ['614.94000000', '0.79800000'], ['614.95000000', '0.69800000'], ['614.96000000', '0.02700000'], ['614.97000000', '3.54400000'], ['614.98000000', '5.55600000']]	\N	\N	2026-02-06 03:55:39.847188
73	BTCUSDT	64453.7	64453.71	0.010000000002037268	[['64453.70000000', '0.00172000'], ['64453.69000000', '0.00009000'], ['64452.16000000', '0.00008000'], ['64451.70000000', '0.00043000'], ['64451.67000000', '0.00027000'], ['64451.40000000', '0.00009000'], ['64451.04000000', '0.00009000'], ['64450.08000000', '0.00008000'], ['64450.01000000', '0.00018000'], ['64450.00000000', '0.03348000'], ['64449.94000000', '0.00016000'], ['64449.57000000', '0.15532000'], ['64449.51000000', '0.00008000'], ['64449.33000000', '0.00008000'], ['64448.92000000', '0.15532000'], ['64448.88000000', '0.00018000'], ['64448.87000000', '0.01026000'], ['64448.86000000', '0.00008000'], ['64448.13000000', '0.00018000'], ['64448.12000000', '0.01018000']]	[['64453.71000000', '3.54112000'], ['64453.72000000', '0.00009000'], ['64454.36000000', '0.00018000'], ['64454.47000000', '0.00008000'], ['64454.94000000', '0.00268000'], ['64455.20000000', '0.00259000'], ['64455.35000000', '0.00008000'], ['64455.43000000', '0.01429000'], ['64455.60000000', '0.06430000'], ['64455.91000000', '0.00008000'], ['64455.96000000', '0.15606000'], ['64455.97000000', '0.01388000'], ['64456.56000000', '0.00250000'], ['64456.75000000', '0.00250000'], ['64456.85000000', '0.02334000'], ['64456.94000000', '0.00017000'], ['64457.40000000', '0.00785000'], ['64457.41000000', '0.08009000'], ['64457.80000000', '0.03052000'], ['64457.98000000', '0.02414000']]	\N	\N	2026-02-06 04:15:48.462639
74	ETHUSDT	1900	1900.01	0.009999999999990905	[['1900.00000000', '1.13360000'], ['1899.99000000', '0.00870000'], ['1899.98000000', '0.00680000'], ['1899.97000000', '0.00280000'], ['1899.96000000', '0.00580000'], ['1899.95000000', '0.00840000'], ['1899.94000000', '0.54440000'], ['1899.93000000', '1.21700000'], ['1899.92000000', '0.00550000'], ['1899.91000000', '0.01100000'], ['1899.90000000', '1.19120000'], ['1899.89000000', '0.00540000'], ['1899.88000000', '0.00270000'], ['1899.87000000', '0.06380000'], ['1899.86000000', '0.38150000'], ['1899.84000000', '0.00300000'], ['1899.82000000', '0.01500000'], ['1899.81000000', '0.00320000'], ['1899.80000000', '0.00270000'], ['1899.79000000', '0.00670000']]	[['1900.01000000', '29.15350000'], ['1900.03000000', '0.00280000'], ['1900.04000000', '0.00280000'], ['1900.05000000', '0.00550000'], ['1900.06000000', '0.00280000'], ['1900.07000000', '0.00280000'], ['1900.08000000', '3.10340000'], ['1900.09000000', '0.00550000'], ['1900.10000000', '3.15900000'], ['1900.11000000', '1.98040000'], ['1900.13000000', '0.37070000'], ['1900.14000000', '0.40000000'], ['1900.15000000', '2.49080000'], ['1900.16000000', '0.05000000'], ['1900.17000000', '0.37070000'], ['1900.18000000', '0.93170000'], ['1900.19000000', '1.04150000'], ['1900.20000000', '0.00270000'], ['1900.21000000', '0.00270000'], ['1900.23000000', '0.37070000']]	\N	\N	2026-02-06 04:15:49.040828
75	SOLUSDT	76.69	76.7	0.010000000000005116	[['76.69000000', '44.22700000'], ['76.68000000', '161.80300000'], ['76.67000000', '594.79500000'], ['76.66000000', '597.35300000'], ['76.65000000', '439.36500000'], ['76.64000000', '491.37200000'], ['76.63000000', '65.78600000'], ['76.62000000', '310.35700000'], ['76.61000000', '842.67100000'], ['76.60000000', '762.26200000'], ['76.59000000', '162.72000000'], ['76.58000000', '95.47200000'], ['76.57000000', '1008.87200000'], ['76.56000000', '80.09200000'], ['76.55000000', '717.68400000'], ['76.54000000', '60.26200000'], ['76.53000000', '661.09600000'], ['76.52000000', '38.07900000'], ['76.51000000', '328.08500000'], ['76.50000000', '927.27500000']]	[['76.70000000', '328.87100000'], ['76.71000000', '215.53600000'], ['76.72000000', '621.79200000'], ['76.73000000', '923.17800000'], ['76.74000000', '2164.14300000'], ['76.75000000', '782.07500000'], ['76.76000000', '996.42500000'], ['76.77000000', '4190.16300000'], ['76.78000000', '8692.52900000'], ['76.79000000', '875.37800000'], ['76.80000000', '1793.08300000'], ['76.81000000', '86.78500000'], ['76.82000000', '275.32000000'], ['76.83000000', '684.97400000'], ['76.84000000', '199.06500000'], ['76.85000000', '556.77000000'], ['76.86000000', '851.74600000'], ['76.87000000', '104.34000000'], ['76.88000000', '269.71700000'], ['76.89000000', '802.12200000']]	\N	\N	2026-02-06 04:15:49.628097
76	BNBUSDT	619.58	619.59	0.009999999999990905	[['619.58000000', '4.53400000'], ['619.57000000', '1.08500000'], ['619.56000000', '0.02700000'], ['619.55000000', '0.01800000'], ['619.54000000', '0.04000000'], ['619.53000000', '0.02600000'], ['619.52000000', '0.02600000'], ['619.51000000', '0.02700000'], ['619.50000000', '0.02800000'], ['619.49000000', '5.55100000'], ['619.48000000', '0.02300000'], ['619.47000000', '17.21500000'], ['619.46000000', '5.40100000'], ['619.45000000', '1.81700000'], ['619.44000000', '0.02800000'], ['619.42000000', '1.69600000'], ['619.41000000', '0.00900000'], ['619.39000000', '3.00000000'], ['619.38000000', '0.04500000'], ['619.37000000', '6.03500000']]	[['619.59000000', '14.35900000'], ['619.60000000', '0.10500000'], ['619.61000000', '4.98400000'], ['619.62000000', '4.88400000'], ['619.63000000', '4.21300000'], ['619.64000000', '10.33100000'], ['619.65000000', '0.00900000'], ['619.66000000', '0.01700000'], ['619.67000000', '0.01300000'], ['619.68000000', '4.16800000'], ['619.69000000', '4.15900000'], ['619.70000000', '2.40600000'], ['619.71000000', '0.00900000'], ['619.72000000', '2.68100000'], ['619.73000000', '0.03000000'], ['619.74000000', '0.02600000'], ['619.75000000', '1.60900000'], ['619.76000000', '4.49700000'], ['619.77000000', '5.34800000'], ['619.78000000', '0.01700000']]	\N	\N	2026-02-06 04:15:50.208254
69	BTCUSDT	64270.83	64270.84	0.00999999999476131	[['64270.83000000', '0.70456000'], ['64270.82000000', '0.00044000'], ['64270.81000000', '0.00035000'], ['64270.28000000', '0.00018000'], ['64270.27000000', '0.01420000'], ['64269.76000000', '0.00008000'], ['64269.63000000', '0.00018000'], ['64269.62000000', '0.01406000'], ['64269.20000000', '0.00008000'], ['64269.17000000', '0.00008000'], ['64268.98000000', '0.00018000'], ['64268.97000000', '0.01421000'], ['64266.37000000', '0.00008000'], ['64266.36000000', '0.00008000'], ['64266.33000000', '0.00300000'], ['64266.22000000', '0.00018000'], ['64266.21000000', '0.00862000'], ['64265.55000000', '0.00008000'], ['64265.27000000', '0.00008000'], ['64265.06000000', '0.00008000']]	[['64270.84000000', '1.41468000'], ['64270.85000000', '0.00044000'], ['64270.86000000', '0.00051000'], ['64271.06000000', '0.00267000'], ['64271.20000000', '0.00267000'], ['64271.79000000', '0.00008000'], ['64272.81000000', '0.00250000'], ['64272.85000000', '0.00008000'], ['64273.16000000', '0.00031000'], ['64273.79000000', '0.00008000'], ['64274.02000000', '0.00008000'], ['64274.10000000', '0.01732000'], ['64274.11000000', '0.00009000'], ['64274.40000000', '0.00016000'], ['64274.42000000', '0.00250000'], ['64274.92000000', '0.03071000'], ['64275.19000000', '0.00250000'], ['64275.33000000', '0.00787000'], ['64275.34000000', '0.00300000'], ['64275.75000000', '0.20993000']]	\N	\N	2026-02-06 04:05:42.290772
70	ETHUSDT	1891.31	1891.32	0.009999999999990905	[['1891.31000000', '9.63570000'], ['1891.30000000', '0.00550000'], ['1891.29000000', '0.00280000'], ['1891.27000000', '0.00280000'], ['1891.26000000', '0.00870000'], ['1891.25000000', '0.00280000'], ['1891.24000000', '0.00610000'], ['1891.20000000', '0.06150000'], ['1891.19000000', '0.00810000'], ['1891.18000000', '0.00840000'], ['1891.17000000', '0.11220000'], ['1891.16000000', '0.00560000'], ['1891.15000000', '8.52880000'], ['1891.14000000', '2.51860000'], ['1891.13000000', '0.01370000'], ['1891.12000000', '1.18950000'], ['1891.11000000', '3.15270000'], ['1891.10000000', '0.00270000'], ['1891.08000000', '0.00890000'], ['1891.07000000', '0.00530000']]	[['1891.32000000', '20.91830000'], ['1891.38000000', '0.00270000'], ['1891.39000000', '0.00560000'], ['1891.40000000', '0.27810000'], ['1891.43000000', '0.00560000'], ['1891.47000000', '0.00270000'], ['1891.50000000', '0.00270000'], ['1891.52000000', '0.05000000'], ['1891.54000000', '0.01080000'], ['1891.55000000', '1.18540000'], ['1891.56000000', '0.00400000'], ['1891.57000000', '0.65840000'], ['1891.58000000', '3.15000000'], ['1891.60000000', '0.00270000'], ['1891.61000000', '0.00540000'], ['1891.62000000', '0.03000000'], ['1891.64000000', '0.51150000'], ['1891.66000000', '1.05970000'], ['1891.67000000', '0.00540000'], ['1891.68000000', '0.05950000']]	\N	\N	2026-02-06 04:05:42.817706
71	SOLUSDT	76.36	76.37	0.010000000000005116	[['76.36000000', '277.44300000'], ['76.35000000', '120.18100000'], ['76.34000000', '578.81800000'], ['76.33000000', '923.03800000'], ['76.32000000', '529.74200000'], ['76.31000000', '1003.07500000'], ['76.30000000', '333.54900000'], ['76.29000000', '290.97400000'], ['76.28000000', '931.75700000'], ['76.27000000', '664.76400000'], ['76.26000000', '247.95000000'], ['76.25000000', '31.63400000'], ['76.24000000', '211.03300000'], ['76.23000000', '775.52500000'], ['76.22000000', '357.38500000'], ['76.21000000', '580.17700000'], ['76.20000000', '449.28800000'], ['76.19000000', '109.29000000'], ['76.18000000', '833.60200000'], ['76.17000000', '181.53500000']]	[['76.37000000', '51.10000000'], ['76.38000000', '151.74500000'], ['76.39000000', '440.62200000'], ['76.40000000', '426.45900000'], ['76.41000000', '682.94500000'], ['76.42000000', '703.11400000'], ['76.43000000', '1066.26800000'], ['76.44000000', '509.69400000'], ['76.45000000', '829.05100000'], ['76.46000000', '902.95300000'], ['76.47000000', '104.75600000'], ['76.48000000', '460.36000000'], ['76.49000000', '810.20400000'], ['76.50000000', '344.86300000'], ['76.51000000', '820.45300000'], ['76.52000000', '943.01100000'], ['76.53000000', '618.59700000'], ['76.54000000', '376.06200000'], ['76.55000000', '721.38000000'], ['76.56000000', '49.62800000']]	\N	\N	2026-02-06 04:05:43.765767
72	BNBUSDT	616.42	616.43	0.009999999999990905	[['616.42000000', '24.44800000'], ['616.41000000', '9.31000000'], ['616.40000000', '5.62000000'], ['616.39000000', '0.02500000'], ['616.38000000', '0.01800000'], ['616.37000000', '2.56000000'], ['616.36000000', '8.55900000'], ['616.35000000', '0.01700000'], ['616.33000000', '1.80000000'], ['616.32000000', '0.01800000'], ['616.31000000', '0.01700000'], ['616.30000000', '0.03000000'], ['616.29000000', '3.29000000'], ['616.28000000', '4.89200000'], ['616.26000000', '1.07600000'], ['616.25000000', '0.82300000'], ['616.24000000', '0.03200000'], ['616.23000000', '2.62800000'], ['616.22000000', '0.02600000'], ['616.20000000', '0.03800000']]	[['616.43000000', '0.04500000'], ['616.44000000', '0.07900000'], ['616.45000000', '0.02700000'], ['616.46000000', '1.43800000'], ['616.47000000', '0.01800000'], ['616.48000000', '0.01300000'], ['616.49000000', '0.01700000'], ['616.50000000', '0.01900000'], ['616.51000000', '0.02600000'], ['616.53000000', '4.90600000'], ['616.54000000', '0.01300000'], ['616.55000000', '0.02600000'], ['616.56000000', '0.73600000'], ['616.57000000', '0.69800000'], ['616.58000000', '2.56800000'], ['616.59000000', '0.81500000'], ['616.60000000', '6.09200000'], ['616.61000000', '0.01700000'], ['616.62000000', '4.75100000'], ['616.63000000', '12.81800000']]	\N	\N	2026-02-06 04:05:44.291155
\.


--
-- Data for Name: p2p_rates; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.p2p_rates (id, avg_buy_price, avg_sell_price, best_buy_price, best_sell_price, spread_percent, offers_count, volume, recorded_at) FROM stdin;
1	45.49144546411007	46.401274373392276	45.39144546411007	46.50127437339228	2	42	3445.5431355969313	2026-02-04 23:29:09.26718
2	45.074966231281536	45.97646555590717	44.974966231281535	46.07646555590717	2	31	2001.0541149683427	2026-02-04 23:44:09.267402
3	44.80128455410918	45.69731024519137	44.70128455410918	45.79731024519137	2	20	1123.503303928576	2026-02-04 23:59:09.267462
4	45.16726398130408	46.07060926093016	45.06726398130408	46.17060926093016	2	50	2793.997099922445	2026-02-05 00:14:09.267497
5	44.84856366972173	45.74553494311616	44.748563669721726	45.845534943116164	2	31	3252.176636572981	2026-02-05 00:29:09.267527
6	45.45804451770352	46.36720540805759	45.35804451770352	46.467205408057595	2	25	1399.0536932108917	2026-02-05 00:44:09.267568
7	44.514237551911876	45.40452230295011	44.414237551911874	45.504522302950114	2	40	4294.138179944217	2026-02-05 00:59:09.267606
8	44.8978880390995	45.79584579988149	44.7978880390995	45.89584579988149	2	24	2355.2469399386146	2026-02-05 01:14:09.26763
9	45.346923787976024	46.25386226373555	45.24692378797602	46.35386226373555	2	20	1830.5961077552079	2026-02-05 01:29:09.267664
10	44.54512089626679	45.43602331419213	44.445120896266786	45.53602331419213	2	34	3489.726950265844	2026-02-05 01:44:09.267688
11	45.41063150022698	46.31884413023152	45.310631500226975	46.41884413023152	2	21	2907.4620704896442	2026-02-05 01:59:09.267712
12	45.24208421277869	46.146925897034265	45.14208421277869	46.24692589703427	2	42	2656.2527512609217	2026-02-05 02:14:09.267738
13	44.999994474209885	45.899994363694084	44.89999447420988	45.999994363694086	2	34	4265.968700062855	2026-02-05 02:29:09.267764
14	44.666899928107334	45.56023792666948	44.56689992810733	45.66023792666948	2	50	1123.0133403857017	2026-02-05 02:44:09.267787
15	44.74403163673118	45.638912269465806	44.64403163673118	45.73891226946581	2	49	4590.246019176424	2026-02-05 02:59:09.267808
16	45.08377483742373	45.98545033417221	44.98377483742373	46.08545033417221	2	23	4635.257452059143	2026-02-05 03:14:09.26783
17	44.80078370580277	45.69679937991883	44.70078370580277	45.79679937991883	2	42	4517.82258552003	2026-02-05 03:29:09.267851
18	45.166357886092264	46.06968504381411	45.06635788609226	46.16968504381411	2	33	4242.281541629576	2026-02-05 03:44:09.267873
19	44.88868043836795	45.78645404713531	44.78868043836795	45.88645404713531	2	21	4321.208354045226	2026-02-05 03:59:09.267894
20	44.97063379587442	45.87004647179191	44.87063379587442	45.97004647179191	2	39	4443.2025548768515	2026-02-05 04:14:09.267915
21	45.09163548863476	45.993468198407456	44.991635488634756	46.09346819840746	2	42	1851.8835452252729	2026-02-05 04:29:09.267936
22	45.17315424551695	46.07661733042729	45.073154245516946	46.17661733042729	2	45	4520.05713774499	2026-02-05 04:44:09.267957
23	44.93120676373409	45.82983089900877	44.83120676373409	45.92983089900877	2	24	4232.910199051576	2026-02-05 04:59:09.267979
24	45.14799181532532	46.05095165163183	45.04799181532532	46.15095165163183	2	24	2979.882886292259	2026-02-05 05:14:09.268
25	44.83753459958368	45.734285291575354	44.737534599583675	45.834285291575355	2	34	4653.213589573739	2026-02-05 05:29:09.268021
26	44.57854347549174	45.470114345001576	44.47854347549174	45.57011434500158	2	42	3484.49507152694	2026-02-05 05:44:09.268042
27	44.72998483406686	45.6245845307482	44.62998483406686	45.7245845307482	2	41	3507.0852599020373	2026-02-05 05:59:09.26807
28	44.54953288169739	45.44052353933134	44.44953288169739	45.54052353933134	2	48	2936.566653236673	2026-02-05 06:14:09.268095
29	44.55240001663698	45.44344801696972	44.45240001663698	45.54344801696972	2	49	2325.674409445313	2026-02-05 06:29:09.268147
30	44.87187586662973	45.76931338396233	44.77187586662973	45.86931338396233	2	34	1834.0125497937397	2026-02-05 06:44:09.268187
31	45.320305534745145	46.22671164544005	45.220305534745144	46.32671164544005	2	28	4370.111323155084	2026-02-05 06:59:09.268208
32	44.51337690738491	45.403644445532606	44.41337690738491	45.50364444553261	2	25	4660.626798977803	2026-02-05 07:14:09.268229
33	44.8454940296573	45.74240391025045	44.7454940296573	45.842403910250454	2	36	2454.481932739743	2026-02-05 07:29:09.26825
34	45.006042556947946	45.906163408086904	44.906042556947945	46.006163408086906	2	33	1549.0727589641601	2026-02-05 07:44:09.268271
35	44.53447456870516	45.42516406007926	44.434474568705156	45.52516406007926	2	26	4907.790671994404	2026-02-05 07:59:09.268293
36	44.959820147130685	45.8590165500733	44.859820147130684	45.9590165500733	2	29	1877.4108952076722	2026-02-05 08:14:09.268314
37	44.79108760949357	45.68690936168345	44.69108760949357	45.78690936168345	2	30	4802.356909706807	2026-02-05 08:29:09.268335
38	45.45359211461357	46.36266395690584	45.35359211461357	46.46266395690584	2	32	1220.488934128308	2026-02-05 08:44:09.268356
39	45.00903958956359	45.909220381354864	44.90903958956359	46.009220381354865	2	29	1156.7948531386137	2026-02-05 08:59:09.268377
40	45.49703924228185	46.40698002712749	45.39703924228185	46.50698002712749	2	31	4744.774013633796	2026-02-05 09:14:09.268398
41	45.493088308027914	46.402950074188475	45.39308830802791	46.502950074188476	2	29	4982.556816617149	2026-02-05 09:29:09.268418
42	44.68699798026711	45.58073793987245	44.58699798026711	45.68073793987245	2	28	4984.039679536632	2026-02-05 09:44:09.268439
43	45.43153380356038	46.34016447963158	45.331533803560376	46.440164479631584	2	44	1285.8925795310067	2026-02-05 09:59:09.268459
44	45.264908379894834	46.17020654749273	45.16490837989483	46.270206547492734	2	43	1777.0148724468163	2026-02-05 10:14:09.268578
45	44.619162821948	45.511546078386964	44.519162821948	45.611546078386965	2	24	3599.472026656097	2026-02-05 10:29:09.268607
46	45.218042844644906	46.122403701537806	45.118042844644904	46.22240370153781	2	34	4665.505058481893	2026-02-05 10:44:09.268636
47	45.12522799090725	46.027732550725396	45.02522799090725	46.1277325507254	2	28	2343.7109597943627	2026-02-05 10:59:09.268658
48	45.26526360288957	46.170568874947364	45.16526360288957	46.270568874947365	2	48	4158.247419868271	2026-02-05 11:14:09.26868
49	44.843074857450816	45.739936354599834	44.743074857450814	45.839936354599836	2	31	4171.087379394263	2026-02-05 11:29:09.268701
50	45.05933089189082	45.96051750972864	44.95933089189082	46.06051750972864	2	35	4967.426048058029	2026-02-05 11:44:09.268722
51	45.20878708273372	46.1129628243884	45.10878708273372	46.2129628243884	2	35	2681.0427526394255	2026-02-05 11:59:09.268743
52	44.934799030199116	45.8334950108031	44.834799030199115	45.9334950108031	2	33	4233.182650892852	2026-02-05 12:14:09.268764
53	44.59754434319682	45.48949523006076	44.49754434319682	45.58949523006076	2	42	2770.129703293095	2026-02-05 12:29:09.268786
54	45.42154540687399	46.32997631501147	45.32154540687399	46.42997631501147	2	48	2515.814724411307	2026-02-05 12:44:09.268807
55	44.54725159558875	45.438196627500524	44.447251595588746	45.538196627500525	2	45	4721.122590875052	2026-02-05 12:59:09.268831
56	45.260380951888465	46.16558857092623	45.16038095188846	46.265588570926234	2	48	1863.795681709091	2026-02-05 13:14:09.268855
57	45.14126658867616	46.04409192044968	45.04126658867616	46.14409192044968	2	50	2801.1691437634736	2026-02-05 13:29:09.268878
58	45.05774540413652	45.95890031221925	44.95774540413652	46.05890031221925	2	49	4942.345384022969	2026-02-05 13:44:09.268903
59	45.06191942052202	45.96315780893246	44.961919420522015	46.06315780893246	2	43	1353.175647100668	2026-02-05 13:59:09.268931
60	45.02409123521503	45.92457305991933	44.92409123521503	46.024573059919334	2	33	1815.882085648905	2026-02-05 14:14:09.268954
61	45.18686307288929	46.09060033434707	45.08686307288929	46.190600334347074	2	30	4835.590649370599	2026-02-05 14:29:09.268976
62	45.23770067299672	46.14245468645666	45.13770067299672	46.24245468645666	2	43	1937.9565849815958	2026-02-05 14:44:09.268998
63	45.25988945064232	46.165087239655165	45.15988945064232	46.265087239655166	2	39	3677.117468034385	2026-02-05 14:59:09.26902
64	44.67217673610005	45.56562027082205	44.57217673610005	45.66562027082205	2	45	3730.6247491483527	2026-02-05 15:14:09.269041
65	44.82261483795653	45.71906713471566	44.72261483795653	45.81906713471566	2	43	4816.486099715017	2026-02-05 15:29:09.269062
66	45.47522494930881	46.38472944829499	45.37522494930881	46.48472944829499	2	22	1967.2431789737902	2026-02-05 15:44:09.269084
67	45.3097872348795	46.21598297957709	45.2097872348795	46.31598297957709	2	39	4068.542560929959	2026-02-05 15:59:09.269105
68	44.89653247887959	45.79446312845719	44.79653247887959	45.89446312845719	2	21	2505.284420204907	2026-02-05 16:14:09.269176
69	45.21491571680606	46.119214031142185	45.11491571680606	46.21921403114219	2	30	2209.680669503441	2026-02-05 16:29:09.269199
70	44.668648877635796	45.56202185518851	44.568648877635795	45.66202185518851	2	27	1124.4444967648183	2026-02-05 16:44:09.269221
71	44.61424905855219	45.506534039723235	44.51424905855219	45.606534039723236	2	24	1953.3354062390247	2026-02-05 16:59:09.269241
72	44.88902131739009	45.78680174373789	44.78902131739009	45.88680174373789	2	37	2753.9466801133008	2026-02-05 17:14:09.269263
73	44.67164216874889	45.56507501212387	44.57164216874889	45.66507501212387	2	20	2465.2923937725495	2026-02-05 17:29:09.269283
74	44.690191501660244	45.58399533169345	44.59019150166024	45.68399533169345	2	46	3942.49475099868	2026-02-05 17:44:09.269304
75	45.39968759317861	46.307681345042184	45.29968759317861	46.407681345042185	2	29	2604.6963025897985	2026-02-05 17:59:09.269325
76	45.48372780767045	46.39340236382386	45.38372780767045	46.49340236382386	2	26	4399.760958968754	2026-02-05 18:14:09.269346
77	44.845967874191466	45.7428872316753	44.745967874191464	45.8428872316753	2	38	2575.1557408756266	2026-02-05 18:29:09.269368
78	44.809328416460424	45.70551498478963	44.70932841646042	45.80551498478963	2	40	2317.461310283627	2026-02-05 18:44:09.269388
79	45.24151527683992	46.14634558237672	45.14151527683992	46.24634558237672	2	43	2634.4939084510233	2026-02-05 18:59:09.269409
80	45.225623753231105	46.130136228295726	45.1256237532311	46.23013622829573	2	39	4215.404804400208	2026-02-05 19:14:09.26943
81	45.405570544996635	46.31368195589657	45.305570544996634	46.41368195589657	2	29	2518.460836901208	2026-02-05 19:29:09.269451
82	45.02230962545639	45.922755817965516	44.922309625456386	46.02275581796552	2	44	2829.597861225788	2026-02-05 19:44:09.269472
83	45.109404167172094	46.011592250515534	45.00940416717209	46.111592250515535	2	41	1634.7540296831946	2026-02-05 19:59:09.269494
84	44.90708909106391	45.80523087288519	44.80708909106391	45.90523087288519	2	21	1493.7066883539815	2026-02-05 20:14:09.269514
85	44.53161048834381	45.422242698110686	44.43161048834381	45.52224269811069	2	39	1871.273459539858	2026-02-05 20:29:09.269535
86	45.12565658799674	46.028169719756676	45.025656587996735	46.12816971975668	2	43	2799.963962674223	2026-02-05 20:44:09.269556
87	45.270728658868876	46.17614323204626	45.170728658868875	46.27614323204626	2	41	4957.412095208187	2026-02-05 20:59:09.269579
88	44.85216243677018	45.749205685505586	44.75216243677018	45.84920568550559	2	44	2468.085738668411	2026-02-05 21:14:09.2696
89	44.51948169875203	45.40987133272707	44.41948169875203	45.50987133272707	2	48	1002.0252508890022	2026-02-05 21:29:09.269622
90	45.294747963498054	46.20064292276802	45.19474796349805	46.30064292276802	2	21	3106.962527443353	2026-02-05 21:44:09.269642
91	44.84657100283212	45.74350242288877	44.74657100283212	45.84350242288877	2	34	1713.2065619697278	2026-02-05 21:59:09.269663
92	45.43907672093952	46.34785825535831	45.33907672093952	46.44785825535831	2	40	2875.5812592934462	2026-02-05 22:14:09.269684
93	45.29743140909806	46.20338003728002	45.19743140909806	46.30338003728002	2	23	1548.0450036407735	2026-02-05 22:29:09.269705
94	45.33108702015209	46.23770876055513	45.23108702015209	46.33770876055513	2	35	2378.0597868314458	2026-02-05 22:44:09.269727
95	45.177683734861674	46.08123740955891	45.07768373486167	46.18123740955891	2	36	3387.964580115092	2026-02-05 22:59:09.269748
96	44.688140280048074	45.58190308564904	44.58814028004807	45.68190308564904	2	42	3633.8639228580514	2026-02-05 23:14:09.269768
\.


--
-- Data for Name: signals; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.signals (id, symbol, type, strength, confidence, entry_price, take_profit, stop_loss, risk_reward, reasoning, ml_data, raw_response, result, actual_pnl, created_at, expires_at, closed_at) FROM stdin;
1	BTCUSDT	LONG	STRONG	87.67646123614233	70000	73500	68600	2.5	["Tendencia fuerte", "RSI en zona óptima", "Alineación MTF"]	{"patterns": ["Hammer", "Engulfing"], "indicators": ["RSI", "MACD"]}	\N	PENDING	\N	2026-02-03 23:29:09.275001	2026-02-06 01:29:09.275027	\N
2	BNBUSDT	SHORT	STRONG	77.67302812622843	150	142.5	153	2.5	["Tendencia fuerte", "RSI en zona óptima", "Alineación MTF"]	{"patterns": ["Hammer", "Engulfing"], "indicators": ["RSI", "MACD"]}	\N	PENDING	\N	2026-02-05 13:29:09.27516	2026-02-06 01:29:09.275166	\N
3	ETHUSDT	LONG	STRONG	80.17862969304977	3500	3675	3430	2.5	["Tendencia fuerte", "RSI en zona óptima", "Alineación MTF"]	{"patterns": ["Hammer", "Engulfing"], "indicators": ["RSI", "MACD"]}	\N	WIN	\N	2026-02-05 20:29:09.275213	2026-02-06 01:29:09.275218	\N
4	SOLUSDT	SHORT	MODERATE	86.0557379107008	150	142.5	153	2.5	["Tendencia fuerte", "RSI en zona óptima", "Alineación MTF"]	{"patterns": ["Hammer", "Engulfing"], "indicators": ["RSI", "MACD"]}	\N	PENDING	\N	2026-02-04 15:29:09.275257	2026-02-06 01:29:09.275261	\N
5	BNBUSDT	SHORT	MODERATE	87.68633064962876	150	142.5	153	2.5	["Tendencia fuerte", "RSI en zona óptima", "Alineación MTF"]	{"patterns": ["Hammer", "Engulfing"], "indicators": ["RSI", "MACD"]}	\N	WIN	\N	2026-02-04 02:29:09.275297	2026-02-06 01:29:09.275301	\N
6	BNBUSDT	SHORT	MODERATE	86.0954903665998	150	142.5	153	2.5	["Tendencia fuerte", "RSI en zona óptima", "Alineación MTF"]	{"patterns": ["Hammer", "Engulfing"], "indicators": ["RSI", "MACD"]}	\N	LOSS	\N	2026-02-05 18:29:09.275336	2026-02-06 01:29:09.275339	\N
7	ETHUSDT	LONG	MODERATE	87.20079270710357	3500	3675	3430	2.5	["Tendencia fuerte", "RSI en zona óptima", "Alineación MTF"]	{"patterns": ["Hammer", "Engulfing"], "indicators": ["RSI", "MACD"]}	\N	PENDING	\N	2026-02-04 16:29:09.275375	2026-02-06 01:29:09.275379	\N
8	BTCUSDT	LONG	STRONG	93.23456989589845	70000	73500	68600	2.5	["Tendencia fuerte", "RSI en zona óptima", "Alineación MTF"]	{"patterns": ["Hammer", "Engulfing"], "indicators": ["RSI", "MACD"]}	\N	LOSS	\N	2026-02-04 05:29:09.275413	2026-02-06 01:29:09.275416	\N
9	BTCUSDT	SHORT	MODERATE	92.40719796101057	70000	66500	71400	2.5	["Tendencia fuerte", "RSI en zona óptima", "Alineación MTF"]	{"patterns": ["Hammer", "Engulfing"], "indicators": ["RSI", "MACD"]}	\N	PENDING	\N	2026-02-05 03:29:09.27545	2026-02-06 01:29:09.275454	\N
10	ETHUSDT	SHORT	MODERATE	82.53496186911525	3500	3325	3570	2.5	["Tendencia fuerte", "RSI en zona óptima", "Alineación MTF"]	{"patterns": ["Hammer", "Engulfing"], "indicators": ["RSI", "MACD"]}	\N	WIN	\N	2026-02-04 14:29:09.275488	2026-02-06 01:29:09.275491	\N
\.


--
-- Data for Name: transactions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.transactions (id, user_id, symbol, side, type, quantity, price, total, order_id, status, created_at) FROM stdin;
\.


--
-- Data for Name: trusted_devices; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.trusted_devices (id, user_id, device_id, user_agent, ip_address, created_at, expires_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, email, name, password_hash, totp_secret, has_2fa, created_at, updated_at, last_login) FROM stdin;
1	admin@sic.com	Administrator	$2b$12$0yXri5VM8D4BAMc2mEKfaug0xd4iqc4pGqW7CPBBljSs/lKDZNEUq	\N	f	2026-02-05 23:15:32.29454	2026-02-06 03:42:55.5303	2026-02-06 03:42:55.528898
\.


--
-- Data for Name: virtual_trades; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.virtual_trades (id, wallet_id, symbol, side, type, strategy, reason, quantity, price, pnl, created_at) FROM stdin;
1	1	AVAXUSDT	BUY	LIMIT	AI_SIGNAL	SL: 8.05, TP: 9.46	5.91715976331361	8.45	0	2026-02-05 23:22:37.172013
2	1	ATOMUSDT	BUY	LIMIT	AI_SIGNAL	SL: 1.74, TP: 2.07	27.3224043715847	1.83	0	2026-02-05 23:36:37.208713
3	1	ATOMUSDT	BUY	LIMIT	AI_SIGNAL	SL: 1.74, TP: 2.07	27.3224043715847	1.83	0	2026-02-06 00:01:30.557922
4	1	SOLUSDT	SELL	LIMIT	AI_SIGNAL	SL: 78.49, TP: 61.16	0.6799020940984498	73.54	0	2026-02-06 00:16:06.301999
5	1	BTCUSDT	SELL	LIMIT	AI_SIGNAL	SL: 63602.66, TP: 53263.39	0.0016488432210614	60648.58	0	2026-02-06 00:20:20.780245
6	1	DOTUSDT	BUY	LIMIT	AI_SIGNAL	SL: 1.07, TP: 1.38	86.20689655172414	1.16	0	2026-02-06 01:22:11.773886
7	1	DOGEUSDT	BUY	LIMIT	AI_SIGNAL	SL: 0.08, TP: 0.1	222.22222222222223	0.09	0	2026-02-06 01:22:34.694163
8	1	LINKUSDT	BUY	LIMIT	AI_SIGNAL	SL: 7.48, TP: 9.26	2.5031289111389237	7.99	0	2026-02-06 01:22:57.85439
\.


--
-- Data for Name: virtual_wallets; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.virtual_wallets (id, user_id, initial_capital, balances, created_at, reset_at) FROM stdin;
1	1	5000	{"USDT": 859.56, "BTC": 0.00835116, "ETH": 0.5, "BNB": 0.1, "SOL": 9.32009791, "XRP": 500.0, "ADA": 1000.0, "DOT": 186.20689655, "MATIC": 100.0, "DOGE": 5222.22222222, "LINK": 52.50312891, "AVAX": 5.91715976, "ATOM": 54.64480874}	2026-02-05 23:15:32.303678	\N
\.


--
-- Data for Name: whale_alerts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.whale_alerts (id, blockchain, tx_hash, amount, amount_usd, from_address, to_address, from_label, to_label, flow_type, sentiment, "timestamp") FROM stdin;
1	ETH	0x3e91c244de4007f59c547a7d3974f5c62bc5776109455a241d513fc3c555d80b	387.54106874710953	38362245.65799618	\N	\N	Whale Wallet	Binance Hot Wallet	whale_to_whale	neutral	2026-02-05 23:26:47.140582
2	BTC	0xa74d23a32965c29d644b8f81f82cde0f0885cbeec1202fa500a8ecd27cc1f51d	172.63794577438114	14602910.265294045	\N	\N	Binance Hot Wallet	Whale Wallet	exchange_outflow	bullish	2026-02-05 12:19:47.140744
3	BTC	0xeeb36ba64033a21085b3128d2cfac2a701e686db08d1861b68590ef7c8f96c41	341.73038202514874	37314700.362519	\N	\N	Whale Wallet	Binance Hot Wallet	whale_to_whale	neutral	2026-02-05 09:48:47.140799
4	BTC	0x2fd5513bd7200968c6289a95a59bd59869505a94387130a4a5cb2c8b056872c2	318.74713421058306	11845845.875249699	\N	\N	Binance Hot Wallet	Whale Wallet	exchange_outflow	bullish	2026-02-05 15:23:47.140837
5	BTC	0x22cc8f51bc77b73be4776b929aa4e8ded3390da814aa1aeeb253320de2eaad19	722.8317230799556	37662159.353677765	\N	\N	Binance Hot Wallet	Whale Wallet	exchange_outflow	bullish	2026-02-05 08:15:47.14087
6	BNB	0xc1efbe22e06965d918d66932ceaaec2e895c645536e1d7fdb147bcb65e349da4	275.409016681563	45827473.082264654	\N	\N	Whale Wallet	Binance Hot Wallet	exchange_inflow	bearish	2026-02-05 11:51:47.140904
7	SOL	0xad78e8b7ffae7ca50a47c8e679181ea89e9934f779226248f51097814506eab1	881.2220861837768	30363137.88092887	\N	\N	Whale Wallet	Binance Hot Wallet	exchange_inflow	bearish	2026-02-05 07:42:47.140936
8	ETH	0xecdcf0c4e4e97488e1bbeab2bb3558bda600fa127384e314ce71407179b93c0b	833.2255030028092	37982065.58819513	\N	\N	Whale Wallet	Binance Hot Wallet	exchange_inflow	bearish	2026-02-05 09:16:47.140965
9	BNB	0xfec6cc9d9ded56747d592f24004e674771fe4519c32790f0e7496313e55bf314	198.99554709039094	24984289.636833053	\N	\N	Binance Hot Wallet	Whale Wallet	exchange_outflow	bullish	2026-02-05 18:18:47.140993
10	BNB	0x2b76e488b5742f731815ea983fb8b8993f8638d5cfc47f76cb9b5337757888ba	540.183480223164	8374400.681386976	\N	\N	Binance Hot Wallet	Whale Wallet	exchange_outflow	bullish	2026-02-05 07:06:47.14102
11	BTC	0x6196bf59fef675f213a8b89994d7fd8916f1c4ab0c4f2eaf1e5fc065762615b4	230.90778369203926	26588625.949133247	\N	\N	Whale Wallet	Binance Hot Wallet	whale_to_whale	neutral	2026-02-05 13:20:47.141047
12	BNB	0x6667971533f1c9ca817f99044bd4d83d93b7bc66aec4ee041351328fb340db87	418.129144012648	20258116.44609902	\N	\N	Whale Wallet	Binance Hot Wallet	exchange_inflow	bearish	2026-02-05 01:30:47.141086
13	BTC	0xc5cefe17009a3ce89bc090d616a9bd0bad982b8d101e8700c76a60d345103c03	270.9044711642156	43137008.57438875	\N	\N	Whale Wallet	Binance Hot Wallet	whale_to_whale	neutral	2026-02-05 21:22:47.141129
14	SOL	0x3ebef2c1ff76680d16c87493c94ba95448616cb270fae53a2949090fed841a16	952.7224349734057	10785561.900524179	\N	\N	Whale Wallet	Binance Hot Wallet	whale_to_whale	neutral	2026-02-05 11:42:47.141164
15	SOL	0xe8bcbd4cda8dfd400b796ca8d7aa3b4beb12b2c7cc409aa5333d66406acd1863	947.2325224652178	16663539.264950976	\N	\N	Whale Wallet	Binance Hot Wallet	exchange_inflow	bearish	2026-02-05 22:12:47.141197
16	BTC	0xe99214ac2ecb331c14005a1123258f86c5df253a8e9d9634a76be681cadbb248	810.4407853308194	24282921.920490883	\N	\N	Whale Wallet	Binance Hot Wallet	whale_to_whale	neutral	2026-02-05 20:53:47.141229
17	ETH	0x58492708fbce0b93969a451ee294f7721c8dfa0e0dc33ffffba6501f7d053d44	134.27500097938588	24053255.580273516	\N	\N	Whale Wallet	Binance Hot Wallet	exchange_inflow	bearish	2026-02-05 01:31:47.141263
18	ETH	0x18e4a88f74056f54e8fb17d2e94d7df78093de673e82228ea42950f9e3971240	828.0904124348526	15084410.284134086	\N	\N	Binance Hot Wallet	Whale Wallet	exchange_outflow	bullish	2026-02-05 17:11:47.141577
19	BTC	0xc2e3679f02bdc73f64740443972d8c8d805a0690fa5e9afd51ab61df1d3c4e65	763.058560159086	6211332.232108754	\N	\N	Binance Hot Wallet	Whale Wallet	exchange_outflow	bullish	2026-02-05 05:39:47.14163
20	BTC	0x14cdde8b4b25903912062324eff2bb835b21532d1d581f6cf0be78eeab0f8772	195.90011312971995	27129566.441121884	\N	\N	Binance Hot Wallet	Whale Wallet	exchange_outflow	bullish	2026-02-05 16:50:47.141667
21	BTC	0xe55765c529b68b5a1396a6e8c31bdc976fd0d6f61989638f0847794d17185ed9	771.1089419358319	18172248.038999416	\N	\N	Whale Wallet	Binance Hot Wallet	exchange_inflow	bearish	2026-02-05 13:36:47.141699
22	SOL	0x328c1abbc83a86442d292138c45dab6d78cae7d782ce5f0c96ec7d546649ca79	664.5762567490094	16987254.60682467	\N	\N	Binance Hot Wallet	Whale Wallet	exchange_outflow	bullish	2026-02-05 13:02:47.14175
23	SOL	0xfe0f2823eb5078d44612b98489de2e7c1d2b8b1326dfda091e7685796a985e88	844.142396939506	44525839.821523234	\N	\N	Binance Hot Wallet	Whale Wallet	exchange_outflow	bullish	2026-02-05 23:00:47.14179
24	ETH	0x3f30e8a9b69fc5cff4c54141eb9cccefe859d0c93985d18361919d37e3c8f355	961.3375251626455	27076289.19370846	\N	\N	Binance Hot Wallet	Whale Wallet	exchange_outflow	bullish	2026-02-05 21:34:47.141829
25	BTC	0x5d154a2dbbcf6a1e9f45a8a94fd07a32b47791801e6cd3760ebe848886475ed4	437.54408569278826	22165912.751653086	\N	\N	Whale Wallet	Binance Hot Wallet	exchange_inflow	bearish	2026-02-05 11:24:47.141861
26	ETH	0xc83041b2e51e9977ac2ee3e7329171c25f2f726abccb0d0c2a2f4a03a57b7f09	616.596486931863	9858599.73381095	\N	\N	Whale Wallet	Binance Hot Wallet	exchange_inflow	bearish	2026-02-05 19:58:47.141897
27	BNB	0x7f0056c7ab0a860c3d476eb49368e39f9f4f74daedca18553911949a92e07624	312.2185984783832	15611540.543664115	\N	\N	Binance Hot Wallet	Whale Wallet	exchange_outflow	bullish	2026-02-05 02:18:47.141928
28	BTC	0x25afb0a2ae9e14ddaa63b7adba75c3e1a52733e394d2be24987851094151efa6	157.35158731654772	32180554.18559869	\N	\N	Whale Wallet	Binance Hot Wallet	whale_to_whale	neutral	2026-02-05 09:19:47.141963
29	ETH	0x3b049040d0732bfe6e3b675eebf7cf90a6a26b81d954fff54b2ca5dcc5e1e575	594.6174627068094	42097905.5781286	\N	\N	Whale Wallet	Binance Hot Wallet	whale_to_whale	neutral	2026-02-05 13:32:47.141995
30	BTC	0xa3947ebece3e881258634c624eaf1f2de5e9b08a0f756e408588cf42aef9e769	524.0449089567778	20596759.950676754	\N	\N	Binance Hot Wallet	Whale Wallet	exchange_outflow	bullish	2026-02-05 03:07:47.142032
31	BNB	0xc722da8f28fa06885b94f683932a8a541215f92dd4a7a23919c889a049c1c19c	3736.8683860570904	106377870.28104573	\N	\N	Whale Wallet	Whale Wallet	whale_to_whale	neutral	2026-02-06 01:33:23.476697
32	SOL	0x08b19932e6da674c8196f8ef607338f67510b3fbbafe90f062468dbb2e594674	3320.520525398626	244918276.5698115	\N	\N	Whale Wallet	Whale Wallet	whale_to_whale	neutral	2026-02-06 01:53:24.622587
33	BTC	0x54dc07384649a29003002c00738bce69ab28ed8a782a23853118f5351ce9d6c0	2003.3689624930698	202067328.23285192	\N	\N	Binance Hot	Binance Hot	exchange_inflow	bearish	2026-02-06 02:23:40.619135
34	ETH	0x50c585be4b2fd3dffc515e2ced33c3642bb9dbd029ed8618fe296807480d223e	3963.8039232097753	126766870.0787148	\N	\N	Whale Wallet	Whale Wallet	whale_to_whale	neutral	2026-02-06 02:46:13.8227
35	BTC	0x1422c6202ddba0f7929cf8f9a597d4f18baa60e136d84ec87794622098f7ca98	2600.220553012068	78743232.91110013	\N	\N	Binance Hot	Binance Hot	exchange_inflow	bearish	2026-02-06 03:25:21.844321
36	ETH	0xac9389fe1d3c10542245ee3171d640797501222cfb767c0fcfaa87daf39a2e58	1202.6935741501854	113295029.0215459	\N	\N	Whale Wallet	Whale Wallet	exchange_outflow	bullish	2026-02-06 03:35:24.766635
37	ETH	0x363307115304e921e58fadd2e84323e7911be6e15c0d3b414627b97854c17739	2879.527020560567	73449695.79458833	\N	\N	Whale Wallet	Whale Wallet	exchange_outflow	bullish	2026-02-06 04:05:44.291414
\.


--
-- Name: agent_trades_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.agent_trades_id_seq', 1, false);


--
-- Name: alerts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.alerts_id_seq', 1, false);


--
-- Name: funding_rate_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.funding_rate_history_id_seq', 76, true);


--
-- Name: journal_entries_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.journal_entries_id_seq', 1, false);


--
-- Name: order_book_snapshots_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.order_book_snapshots_id_seq', 76, true);


--
-- Name: p2p_rates_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.p2p_rates_id_seq', 96, true);


--
-- Name: signals_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.signals_id_seq', 10, true);


--
-- Name: transactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.transactions_id_seq', 1, false);


--
-- Name: trusted_devices_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.trusted_devices_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 1, true);


--
-- Name: virtual_trades_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.virtual_trades_id_seq', 8, true);


--
-- Name: virtual_wallets_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.virtual_wallets_id_seq', 1, true);


--
-- Name: whale_alerts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.whale_alerts_id_seq', 37, true);


--
-- Name: agent_trades agent_trades_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_trades
    ADD CONSTRAINT agent_trades_pkey PRIMARY KEY (id);


--
-- Name: alerts alerts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alerts
    ADD CONSTRAINT alerts_pkey PRIMARY KEY (id);


--
-- Name: funding_rate_history funding_rate_history_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.funding_rate_history
    ADD CONSTRAINT funding_rate_history_pkey PRIMARY KEY (id);


--
-- Name: journal_entries journal_entries_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.journal_entries
    ADD CONSTRAINT journal_entries_pkey PRIMARY KEY (id);


--
-- Name: order_book_snapshots order_book_snapshots_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_book_snapshots
    ADD CONSTRAINT order_book_snapshots_pkey PRIMARY KEY (id);


--
-- Name: p2p_rates p2p_rates_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.p2p_rates
    ADD CONSTRAINT p2p_rates_pkey PRIMARY KEY (id);


--
-- Name: signals signals_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.signals
    ADD CONSTRAINT signals_pkey PRIMARY KEY (id);


--
-- Name: transactions transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_pkey PRIMARY KEY (id);


--
-- Name: trusted_devices trusted_devices_device_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trusted_devices
    ADD CONSTRAINT trusted_devices_device_id_key UNIQUE (device_id);


--
-- Name: trusted_devices trusted_devices_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trusted_devices
    ADD CONSTRAINT trusted_devices_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: virtual_trades virtual_trades_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.virtual_trades
    ADD CONSTRAINT virtual_trades_pkey PRIMARY KEY (id);


--
-- Name: virtual_wallets virtual_wallets_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.virtual_wallets
    ADD CONSTRAINT virtual_wallets_pkey PRIMARY KEY (id);


--
-- Name: virtual_wallets virtual_wallets_user_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.virtual_wallets
    ADD CONSTRAINT virtual_wallets_user_id_key UNIQUE (user_id);


--
-- Name: whale_alerts whale_alerts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.whale_alerts
    ADD CONSTRAINT whale_alerts_pkey PRIMARY KEY (id);


--
-- Name: whale_alerts whale_alerts_tx_hash_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.whale_alerts
    ADD CONSTRAINT whale_alerts_tx_hash_key UNIQUE (tx_hash);


--
-- Name: ix_agent_trades_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_agent_trades_id ON public.agent_trades USING btree (id);


--
-- Name: ix_agent_trades_trade_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_agent_trades_trade_id ON public.agent_trades USING btree (trade_id);


--
-- Name: ix_funding_rate_history_symbol; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_funding_rate_history_symbol ON public.funding_rate_history USING btree (symbol);


--
-- Name: ix_funding_rate_history_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_funding_rate_history_timestamp ON public.funding_rate_history USING btree ("timestamp");


--
-- Name: ix_order_book_snapshots_symbol; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_order_book_snapshots_symbol ON public.order_book_snapshots USING btree (symbol);


--
-- Name: ix_order_book_snapshots_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_order_book_snapshots_timestamp ON public.order_book_snapshots USING btree ("timestamp");


--
-- Name: ix_p2p_rates_recorded_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_p2p_rates_recorded_at ON public.p2p_rates USING btree (recorded_at);


--
-- Name: ix_signals_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_signals_id ON public.signals USING btree (id);


--
-- Name: ix_transactions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_transactions_id ON public.transactions USING btree (id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: ix_virtual_trades_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_virtual_trades_id ON public.virtual_trades USING btree (id);


--
-- Name: ix_whale_alerts_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_whale_alerts_timestamp ON public.whale_alerts USING btree ("timestamp");


--
-- Name: alerts alerts_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alerts
    ADD CONSTRAINT alerts_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: journal_entries journal_entries_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.journal_entries
    ADD CONSTRAINT journal_entries_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: transactions transactions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: trusted_devices trusted_devices_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trusted_devices
    ADD CONSTRAINT trusted_devices_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: virtual_trades virtual_trades_wallet_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.virtual_trades
    ADD CONSTRAINT virtual_trades_wallet_id_fkey FOREIGN KEY (wallet_id) REFERENCES public.virtual_wallets(id);


--
-- Name: virtual_wallets virtual_wallets_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.virtual_wallets
    ADD CONSTRAINT virtual_wallets_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

\unrestrict 5WxBnWnbJnjiBuAZFfd9UIKXrqqKhAY5tcZKtaLPp7bswIya0nf65JGBr3nwR1n

