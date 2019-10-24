--
-- PostgreSQL database dump
--

-- Dumped from database version 11.5
-- Dumped by pg_dump version 11.5

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

SET default_with_oids = false;

--
-- Name: django_migrations; Type: TABLE; Schema: public; Owner: django
--

CREATE TABLE public.django_migrations (
    id integer NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


ALTER TABLE public.django_migrations OWNER TO django;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: django
--

CREATE SEQUENCE public.django_migrations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_migrations_id_seq OWNER TO django;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: django
--

ALTER SEQUENCE public.django_migrations_id_seq OWNED BY public.django_migrations.id;


--
-- Name: django_migrations id; Type: DEFAULT; Schema: public; Owner: django
--

ALTER TABLE ONLY public.django_migrations ALTER COLUMN id SET DEFAULT nextval('public.django_migrations_id_seq'::regclass);


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: django
--

COPY public.django_migrations (id, app, name, applied) FROM stdin;
1	contenttypes	0001_initial	2019-10-24 15:09:40.545037+02
2	contenttypes	0002_remove_content_type_name	2019-10-24 15:09:40.598431+02
3	auth	0001_initial	2019-10-24 15:09:40.671532+02
4	auth	0002_alter_permission_name_max_length	2019-10-24 15:09:40.803784+02
5	auth	0003_alter_user_email_max_length	2019-10-24 15:09:40.850093+02
6	auth	0004_alter_user_username_opts	2019-10-24 15:09:40.87472+02
7	auth	0005_alter_user_last_login_null	2019-10-24 15:09:40.916686+02
8	auth	0006_require_contenttypes_0002	2019-10-24 15:09:40.930942+02
9	auth	0007_alter_validators_add_error_messages	2019-10-24 15:09:40.976488+02
10	auth	0008_alter_user_username_max_length	2019-10-24 15:09:40.993653+02
11	auth	0009_alter_user_last_name_max_length	2019-10-24 15:09:41.045936+02
12	auth	0010_alter_group_name_max_length	2019-10-24 15:09:41.069723+02
13	auth	0011_update_proxy_permissions	2019-10-24 15:09:41.116061+02
14	a4_candy_users	0001_initial	2019-10-24 15:09:41.206338+02
15	a4_candy_organisations	0001_initial	2019-10-24 15:09:41.36416+02
16	a4projects	0001_initial	2019-10-24 15:09:41.59787+02
17	a4modules	0001_initial	2019-10-24 15:09:41.796516+02
18	a4modules	0002_default_ordering_weight	2019-10-24 15:09:41.947879+02
19	a4modules	0003_rm_unique_name	2019-10-24 15:09:42.074167+02
20	a4modules	0004_description_maxlength_512	2019-10-24 15:09:42.135941+02
21	a4_candy_activities	0001_initial	2019-10-24 15:09:42.195618+02
22	a4labels	0001_initial	2019-10-24 15:09:42.271852+02
23	a4categories	0001_initial	2019-10-24 15:09:42.342468+02
24	a4categories	0002_category_icon	2019-10-24 15:09:42.39273+02
25	a4_candy_moderatorfeedback	0001_initial	2019-10-24 15:09:42.48263+02
26	a4_candy_budgeting	0001_initial	2019-10-24 15:09:42.55017+02
27	wagtailcore	0001_initial	2019-10-24 15:09:43.180564+02
28	wagtailcore	0002_initial_data	2019-10-24 15:09:43.181604+02
29	wagtailcore	0003_add_uniqueness_constraint_on_group_page_permission	2019-10-24 15:09:43.182582+02
30	wagtailcore	0004_page_locked	2019-10-24 15:09:43.183525+02
31	wagtailcore	0005_add_page_lock_permission_to_moderators	2019-10-24 15:09:43.184505+02
32	wagtailcore	0006_add_lock_page_permission	2019-10-24 15:09:43.185648+02
33	wagtailcore	0007_page_latest_revision_created_at	2019-10-24 15:09:43.186815+02
34	wagtailcore	0008_populate_latest_revision_created_at	2019-10-24 15:09:43.187965+02
35	wagtailcore	0009_remove_auto_now_add_from_pagerevision_created_at	2019-10-24 15:09:43.189074+02
36	wagtailcore	0010_change_page_owner_to_null_on_delete	2019-10-24 15:09:43.190164+02
37	wagtailcore	0011_page_first_published_at	2019-10-24 15:09:43.191671+02
38	wagtailcore	0012_extend_page_slug_field	2019-10-24 15:09:43.193548+02
39	wagtailcore	0013_update_golive_expire_help_text	2019-10-24 15:09:43.195335+02
40	wagtailcore	0014_add_verbose_name	2019-10-24 15:09:43.197047+02
41	wagtailcore	0015_add_more_verbose_names	2019-10-24 15:09:43.198746+02
42	wagtailcore	0016_change_page_url_path_to_text_field	2019-10-24 15:09:43.200571+02
43	wagtailcore	0017_change_edit_page_permission_description	2019-10-24 15:09:43.374649+02
44	wagtailcore	0018_pagerevision_submitted_for_moderation_index	2019-10-24 15:09:43.406598+02
45	wagtailcore	0019_verbose_names_cleanup	2019-10-24 15:09:43.545028+02
46	wagtailcore	0020_add_index_on_page_first_published_at	2019-10-24 15:09:43.592062+02
47	wagtailcore	0021_capitalizeverbose	2019-10-24 15:09:44.183479+02
48	wagtailcore	0022_add_site_name	2019-10-24 15:09:44.237983+02
49	wagtailcore	0023_alter_page_revision_on_delete_behaviour	2019-10-24 15:09:44.271719+02
50	wagtailcore	0024_collection	2019-10-24 15:09:44.339221+02
51	wagtailcore	0025_collection_initial_data	2019-10-24 15:09:44.409964+02
52	wagtailcore	0026_group_collection_permission	2019-10-24 15:09:44.501677+02
53	wagtailcore	0027_fix_collection_path_collation	2019-10-24 15:09:44.604473+02
54	wagtailcore	0024_alter_page_content_type_on_delete_behaviour	2019-10-24 15:09:44.670523+02
55	wagtailcore	0028_merge	2019-10-24 15:09:44.680328+02
56	wagtailcore	0029_unicode_slugfield_dj19	2019-10-24 15:09:44.720939+02
57	wagtailcore	0030_index_on_pagerevision_created_at	2019-10-24 15:09:44.788413+02
58	wagtailcore	0031_add_page_view_restriction_types	2019-10-24 15:09:44.904467+02
59	wagtailcore	0032_add_bulk_delete_page_permission	2019-10-24 15:09:44.98057+02
60	wagtailcore	0033_remove_golive_expiry_help_text	2019-10-24 15:09:45.057073+02
61	wagtailcore	0034_page_live_revision	2019-10-24 15:09:45.113929+02
62	wagtailcore	0035_page_last_published_at	2019-10-24 15:09:45.171266+02
63	wagtailcore	0036_populate_page_last_published_at	2019-10-24 15:09:45.272983+02
64	wagtailcore	0037_set_page_owner_editable	2019-10-24 15:09:45.340422+02
65	wagtailcore	0038_make_first_published_at_editable	2019-10-24 15:09:45.44904+02
66	wagtailcore	0039_collectionviewrestriction	2019-10-24 15:09:45.617653+02
67	wagtailcore	0040_page_draft_title	2019-10-24 15:09:45.776536+02
68	wagtailcore	0041_group_collection_permissions_verbose_name_plural	2019-10-24 15:09:45.828578+02
69	taggit	0001_initial	2019-10-24 15:09:45.946456+02
70	taggit	0002_auto_20150616_2121	2019-10-24 15:09:46.031665+02
71	a4_candy_cms_images	0001_initial	2019-10-24 15:09:46.255425+02
72	a4_candy_cms_contacts	0001_initial	2019-10-24 15:09:46.492033+02
73	a4_candy_cms_news	0001_initial	2019-10-24 15:09:46.647415+02
74	a4_candy_cms_pages	0001_initial	2019-10-24 15:09:46.887647+02
75	a4_candy_cms_settings	0001_initial	2019-10-24 15:09:47.089576+02
76	a4_candy_cms_use_cases	0001_initial	2019-10-24 15:09:47.263305+02
77	a4_candy_documents	0001_initial	2019-10-24 15:09:47.410686+02
78	a4_candy_ideas	0001_initial	2019-10-24 15:09:47.538252+02
79	a4_candy_questions	0001_initial	2019-10-24 15:09:47.701493+02
80	a4_candy_likes	0001_initial	2019-10-24 15:09:47.830036+02
81	a4_candy_mapideas	0001_initial	2019-10-24 15:09:47.95132+02
82	a4_candy_maps	0001_initial	2019-10-24 15:09:48.071152+02
83	a4_candy_moderatorremark	0001_initial	2019-10-24 15:09:48.159317+02
84	a4projects	0002_change_to_configured_image_field	2019-10-24 15:09:48.272282+02
85	a4projects	0003_auto_20170130_0836	2019-10-24 15:09:48.448882+02
86	a4projects	0004_project_is_archived	2019-10-24 15:09:48.526892+02
87	a4projects	0005_auto_20170313_1407	2019-10-24 15:09:48.609295+02
88	a4projects	0006_project_typ	2019-10-24 15:09:48.641237+02
89	a4projects	0007_add_verbose_names	2019-10-24 15:09:48.704831+02
90	a4projects	0008_project_tile_image	2019-10-24 15:09:48.744968+02
91	a4projects	0009_optional_info	2019-10-24 15:09:48.810493+02
92	a4projects	0010_image_copyrights	2019-10-24 15:09:48.896602+02
93	a4projects	0011_fix_copyright_field_desc	2019-10-24 15:09:48.995316+02
94	a4projects	0012_remove_project_typ	2019-10-24 15:09:49.039768+02
95	a4projects	0013_help_texts	2019-10-24 15:09:49.13086+02
96	a4projects	0014_collapsible_information_field	2019-10-24 15:09:49.17272+02
97	a4projects	0015_add_contact_fields	2019-10-24 15:09:49.330769+02
98	a4projects	0016_add_verbose_for_contact	2019-10-24 15:09:49.395411+02
99	a4projects	0017_contact_phone_regex	2019-10-24 15:09:49.457063+02
202	wagtailsearch	0001_initial	2019-10-24 15:10:00.761024+02
100	a4administrative_districts	0001_initial	2019-10-24 15:09:49.50638+02
101	a4projects	0018_add_location_and_topic	2019-10-24 15:09:49.612463+02
102	a4projects	0019_rename_topic_field	2019-10-24 15:09:49.688481+02
103	a4projects	0020_update_verbose_name	2019-10-24 15:09:49.727688+02
104	a4projects	0021_names_and_help_topics_and_point	2019-10-24 15:09:49.936703+02
105	a4projects	0022_project_group	2019-10-24 15:09:49.980457+02
106	a4projects	0023_groups_allow_blank	2019-10-24 15:09:50.062514+02
107	a4projects	0024_group_on_delete_set_null	2019-10-24 15:09:50.112189+02
108	a4_candy_newsletters	0001_initial	2019-10-24 15:09:50.213514+02
109	a4_candy_offlineevents	0001_initial	2019-10-24 15:09:50.354035+02
110	a4_candy_partners	0001_initial	2019-10-24 15:09:50.473028+02
111	a4_candy_polls	0001_initial	2019-10-24 15:09:50.721061+02
112	a4_candy_projects	0001_initial	2019-10-24 15:09:50.910594+02
113	a4actions	0001_initial	2019-10-24 15:09:51.039935+02
114	a4actions	0002_add_START_verb	2019-10-24 15:09:51.182968+02
115	a4actions	0003_set_default_ordering_to_timestamp	2019-10-24 15:09:51.23738+02
116	a4actions	0004_auto_20181204_1650	2019-10-24 15:09:51.336683+02
117	a4comments	0001_initial	2019-10-24 15:09:51.421965+02
118	a4comments	0002_extend_comments_field	2019-10-24 15:09:51.525347+02
119	a4comments	0003_comment_comment_categories	2019-10-24 15:09:51.577853+02
120	a4comments	0004_comment_char_limit_increase	2019-10-24 15:09:51.769065+02
121	a4comments	0005_auto_20181204_1641	2019-10-24 15:09:51.832655+02
122	a4comments	0006_comment_last_discussed	2019-10-24 15:09:51.929718+02
123	a4comments	0007_comment_is_moderator_marked	2019-10-24 15:09:52.007613+02
124	a4follows	0001_initial	2019-10-24 15:09:52.144092+02
125	a4maps	0001_initial	2019-10-24 15:09:52.251114+02
126	a4maps	0002_change_help_text	2019-10-24 15:09:52.308254+02
127	a4organisations	0001_initial	2019-10-24 15:09:52.322136+02
128	a4organisations	0002_organisation_slug	2019-10-24 15:09:52.358465+02
129	a4phases	0001_initial	2019-10-24 15:09:52.477261+02
130	a4phases	0002_phase_weight	2019-10-24 15:09:52.541742+02
131	a4phases	0003_fill_weight_field	2019-10-24 15:09:52.640132+02
132	a4phases	0004_change_order	2019-10-24 15:09:52.688478+02
133	a4phases	0005_add_verbose_names	2019-10-24 15:09:52.782255+02
134	a4phases	0006_remove_weight_from_phase_type	2019-10-24 15:09:52.902367+02
135	a4ratings	0001_initial	2019-10-24 15:09:53.097145+02
136	a4ratings	0002_use_usergenerated_content_base_model	2019-10-24 15:09:53.406962+02
137	a4ratings	0003_auto_20181204_1309	2019-10-24 15:09:53.497767+02
138	a4reports	0001_initial	2019-10-24 15:09:53.603087+02
139	a4reports	0002_auto_20181204_1650	2019-10-24 15:09:53.784399+02
140	account	0001_initial	2019-10-24 15:09:53.951141+02
141	account	0002_email_max_length	2019-10-24 15:09:54.043774+02
142	admin	0001_initial	2019-10-24 15:09:54.166049+02
143	admin	0002_logentry_remove_auto_add	2019-10-24 15:09:54.249346+02
144	admin	0003_logentry_add_action_flag_choices	2019-10-24 15:09:54.330239+02
145	background_task	0001_initial	2019-10-24 15:09:54.555936+02
146	background_task	0002_auto_20170927_1109	2019-10-24 15:09:55.37111+02
147	easy_thumbnails	0001_initial	2019-10-24 15:09:55.583905+02
148	easy_thumbnails	0002_thumbnaildimensions	2019-10-24 15:09:55.739736+02
149	sessions	0001_initial	2019-10-24 15:09:55.818587+02
150	sites	0001_initial	2019-10-24 15:09:55.87064+02
151	sites	0002_alter_domain_unique	2019-10-24 15:09:55.929875+02
152	socialaccount	0001_initial	2019-10-24 15:09:56.320911+02
153	socialaccount	0002_token_max_lengths	2019-10-24 15:09:56.481762+02
154	socialaccount	0003_extra_data_default_dict	2019-10-24 15:09:56.510405+02
155	wagtailadmin	0001_create_admin_access_permissions	2019-10-24 15:09:56.655046+02
156	wagtaildocs	0001_initial	2019-10-24 15:09:56.811738+02
157	wagtaildocs	0002_initial_data	2019-10-24 15:09:57.011498+02
158	wagtaildocs	0003_add_verbose_names	2019-10-24 15:09:57.164556+02
159	wagtaildocs	0004_capitalizeverbose	2019-10-24 15:09:57.585288+02
160	wagtaildocs	0005_document_collection	2019-10-24 15:09:57.663383+02
161	wagtaildocs	0006_copy_document_permissions_to_collections	2019-10-24 15:09:57.836718+02
162	wagtaildocs	0005_alter_uploaded_by_user_on_delete_action	2019-10-24 15:09:57.96645+02
163	wagtaildocs	0007_merge	2019-10-24 15:09:57.976553+02
164	wagtaildocs	0008_document_file_size	2019-10-24 15:09:58.074263+02
165	wagtaildocs	0009_document_verbose_name_plural	2019-10-24 15:09:58.149377+02
166	wagtaildocs	0010_document_file_hash	2019-10-24 15:09:58.235017+02
167	wagtailembeds	0001_initial	2019-10-24 15:09:58.293762+02
168	wagtailembeds	0002_add_verbose_names	2019-10-24 15:09:58.339912+02
169	wagtailembeds	0003_capitalizeverbose	2019-10-24 15:09:58.358669+02
170	wagtailembeds	0004_embed_verbose_name_plural	2019-10-24 15:09:58.397386+02
171	wagtailembeds	0005_specify_thumbnail_url_max_length	2019-10-24 15:09:58.429595+02
172	wagtailforms	0001_initial	2019-10-24 15:09:58.553372+02
173	wagtailforms	0002_add_verbose_names	2019-10-24 15:09:58.611828+02
174	wagtailforms	0003_capitalizeverbose	2019-10-24 15:09:58.68239+02
175	wagtailimages	0001_initial	2019-10-24 15:09:59.214839+02
176	wagtailimages	0002_initial_data	2019-10-24 15:09:59.216409+02
177	wagtailimages	0003_fix_focal_point_fields	2019-10-24 15:09:59.218013+02
178	wagtailimages	0004_make_focal_point_key_not_nullable	2019-10-24 15:09:59.220168+02
179	wagtailimages	0005_make_filter_spec_unique	2019-10-24 15:09:59.22236+02
180	wagtailimages	0006_add_verbose_names	2019-10-24 15:09:59.224613+02
181	wagtailimages	0007_image_file_size	2019-10-24 15:09:59.226796+02
182	wagtailimages	0008_image_created_at_index	2019-10-24 15:09:59.228846+02
183	wagtailimages	0009_capitalizeverbose	2019-10-24 15:09:59.230909+02
184	wagtailimages	0010_change_on_delete_behaviour	2019-10-24 15:09:59.232954+02
185	wagtailimages	0011_image_collection	2019-10-24 15:09:59.234976+02
186	wagtailimages	0012_copy_image_permissions_to_collections	2019-10-24 15:09:59.236687+02
187	wagtailimages	0013_make_rendition_upload_callable	2019-10-24 15:09:59.23843+02
188	wagtailimages	0014_add_filter_spec_field	2019-10-24 15:09:59.240554+02
189	wagtailimages	0015_fill_filter_spec_field	2019-10-24 15:09:59.242575+02
190	wagtailimages	0016_deprecate_rendition_filter_relation	2019-10-24 15:09:59.244569+02
191	wagtailimages	0017_reduce_focal_point_key_max_length	2019-10-24 15:09:59.246647+02
192	wagtailimages	0018_remove_rendition_filter	2019-10-24 15:09:59.248659+02
193	wagtailimages	0019_delete_filter	2019-10-24 15:09:59.250824+02
194	wagtailimages	0020_add-verbose-name	2019-10-24 15:09:59.252912+02
195	wagtailimages	0021_image_file_hash	2019-10-24 15:09:59.255057+02
196	wagtailredirects	0001_initial	2019-10-24 15:09:59.452266+02
197	wagtailredirects	0002_add_verbose_names	2019-10-24 15:09:59.650852+02
198	wagtailredirects	0003_make_site_field_editable	2019-10-24 15:09:59.760629+02
199	wagtailredirects	0004_set_unique_on_path_and_site	2019-10-24 15:09:59.91695+02
200	wagtailredirects	0005_capitalizeverbose	2019-10-24 15:10:00.441964+02
201	wagtailredirects	0006_redirect_increase_max_length	2019-10-24 15:10:00.514402+02
203	wagtailsearch	0002_add_verbose_names	2019-10-24 15:10:00.97042+02
204	wagtailsearch	0003_remove_editors_pick	2019-10-24 15:10:01.082431+02
205	wagtailsearch	0004_querydailyhits_verbose_name_plural	2019-10-24 15:10:01.105928+02
206	wagtailusers	0001_initial	2019-10-24 15:10:01.388641+02
207	wagtailusers	0002_add_verbose_name_on_userprofile	2019-10-24 15:10:01.531195+02
208	wagtailusers	0003_add_verbose_names	2019-10-24 15:10:01.615878+02
209	wagtailusers	0004_capitalizeverbose	2019-10-24 15:10:01.801384+02
210	wagtailusers	0005_make_related_name_wagtail_specific	2019-10-24 15:10:01.906058+02
211	wagtailusers	0006_userprofile_prefered_language	2019-10-24 15:10:01.979607+02
212	wagtailusers	0007_userprofile_current_time_zone	2019-10-24 15:10:02.060849+02
213	wagtailusers	0008_userprofile_avatar	2019-10-24 15:10:02.138901+02
214	wagtailusers	0009_userprofile_verbose_name_plural	2019-10-24 15:10:02.228082+02
215	wagtailimages	0001_squashed_0021	2019-10-24 15:10:02.241825+02
216	wagtailcore	0001_squashed_0016_change_page_url_path_to_text_field	2019-10-24 15:10:02.271648+02
\.


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: django
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 216, true);


--
-- Name: django_migrations django_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: django
--

ALTER TABLE ONLY public.django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

