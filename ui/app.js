const state = {
  config: null,
  lists: [],
  status: null,
  speedHistory: [],
  maxHistory: 60,
  logType: "access",
  rules: [],
};

const translations = {
  en: {
    nav_dashboard: "Dashboard",
    nav_unlock: "Unlock Lists",
    nav_settings: "Settings",
    nav_about: "About",
    nav_rules: "Rules",
    nav_diagnostics: "Diagnostics",
    nav_logs: "Logs",
    nav_advanced: "Advanced",
    subtitle: "Smooth DPI bypass, curated by your own lists.",
    card_proxy_status: "Proxy Status",
    card_active_port: "Active Port",
    card_unlocked_lists: "Unlocked Lists",
    card_enabled_lists: "Enabled lists",
    card_fragment_method: "Fragment Method",
    card_sni_strategy: "SNI strategy",
    card_connections: "Connections",
    card_efficiency: "Efficiency",
    card_efficiency_meta: "Unblocked / total",
    card_live_speed: "Live Speed",
    card_traffic_graph: "Traffic Graph",
    card_quick_actions: "Quick Actions",
    btn_refresh_lists: "Refresh Lists",
    btn_open_unlocked: "Open unlocked/",
    btn_open_blacklist: "Open GUI blacklist",
    btn_fullscreen: "Fullscreen",
    btn_compact: "Compact",
    btn_reset_window: "Reset Size",
    unlock_title: "Unlock Lists",
    unlock_subtitle: "Each list is stored in `unlocked/` as a `.txt` file.",
    add_new_website: "Add New Website",
    label_list_name: "List name",
    label_domains: "Domains (one per line)",
    btn_add_list: "Add List",
    settings_title: "Settings",
    settings_subtitle: "Configure ports, language, and custom domains.",
    card_proxy_network: "Proxy Network",
    label_host: "Host",
    label_port: "Port",
    btn_save_network: "Save Network",
    card_language: "Language",
    label_language: "Interface language",
    btn_save_language: "Save Language",
    lang_auto: "Auto (system)",
    card_window: "Window",
    card_custom_domains: "Custom Domains",
    label_custom_domains: "Domains (one per line)",
    btn_save_custom: "Save Custom Domains",
    about_title: "About BlackKittenproxy",
    about_subtitle: "Desktop control center for your DPI-bypass proxy.",
    about_what_title: "What it does",
    about_what_body:
      "BlackKittenproxy wraps the NoDPI engine with a modern control room. Toggle curated unlock lists, apply custom domains, and manage your proxy port with a single click.",
    about_lists_title: "Lists + Custom Domains",
    about_lists_body:
      "Each `.txt` file in `unlocked/` becomes a curated list. Enable the lists you want, and BlackKittenproxy will build a fresh blacklist file for the proxy.",
    about_design_title: "Design cues",
    about_design_body:
      "The layout takes inspiration from VPN dashboards like AmneziaVPN, with an atmospheric gradient, bold typography, and confident controls.",
    rules_title: "Rules",
    rules_subtitle: "Override fragmentation per domain.",
    rules_list: "Rule List",
    rules_add: "Add Rule",
    rules_domain: "Domain / Pattern",
    rules_action: "Action",
    rules_method: "Fragment Method",
    rules_add_btn: "Add Rule",
    diag_title: "Diagnostics",
    diag_subtitle: "Quick health checks for the proxy and lists.",
    diag_running: "Proxy Running",
    diag_port: "Port Open",
    diag_stats_age: "Stats Age",
    diag_blacklist: "Blacklist Entries",
    diag_lists: "List Files",
    diag_actions: "Actions",
    diag_run: "Run Diagnostics",
    logs_title: "Logs",
    logs_subtitle: "Latest access and error logs from the proxy.",
    logs_controls: "Log Controls",
    logs_access: "Access Log",
    logs_error: "Error Log",
    logs_refresh: "Refresh",
    adv_title: "Advanced",
    adv_subtitle: "Fine-tune fragmentation and matching behavior.",
    adv_mode: "Mode",
    adv_mode_label: "Profile",
    adv_fragment: "Fragment Method",
    adv_fragment_label: "Method",
    adv_matching: "Domain Matching",
    adv_matching_label: "Mode",
    adv_flags: "Flags",
    adv_auto_blacklist: "Auto blacklist",
    adv_no_blacklist: "No blacklist (apply to all)",
    adv_save: "Save Advanced",
  },
  ru: {
    nav_dashboard: "Панель",
    nav_unlock: "Списки",
    nav_settings: "Настройки",
    nav_about: "О приложении",
    nav_rules: "Правила",
    nav_diagnostics: "Диагностика",
    nav_logs: "Логи",
    nav_advanced: "Расширенные",
    subtitle: "Плавный DPI‑байпас на ваших списках.",
    card_proxy_status: "Статус прокси",
    card_active_port: "Активный порт",
    card_unlocked_lists: "Списки",
    card_enabled_lists: "Включено",
    card_fragment_method: "Метод фрагментации",
    card_sni_strategy: "SNI стратегия",
    card_connections: "Соединения",
    card_efficiency: "Эффективность",
    card_efficiency_meta: "Разблокировано / всего",
    card_live_speed: "Скорость",
    card_traffic_graph: "График трафика",
    card_quick_actions: "Быстрые действия",
    btn_refresh_lists: "Обновить списки",
    btn_open_unlocked: "Открыть unlocked/",
    btn_open_blacklist: "Открыть GUI blacklist",
    btn_fullscreen: "Полный экран",
    btn_compact: "Компактно",
    btn_reset_window: "Сбросить размер",
    unlock_title: "Списки разблокировки",
    unlock_subtitle: "Каждый список хранится в `unlocked/` как `.txt` файл.",
    add_new_website: "Добавить сайт",
    label_list_name: "Имя списка",
    label_domains: "Домены (по одному в строке)",
    btn_add_list: "Добавить",
    settings_title: "Настройки",
    settings_subtitle: "Порты, язык и пользовательские домены.",
    card_proxy_network: "Сеть прокси",
    label_host: "Хост",
    label_port: "Порт",
    btn_save_network: "Сохранить",
    card_language: "Язык",
    label_language: "Язык интерфейса",
    btn_save_language: "Сохранить",
    lang_auto: "Авто (система)",
    card_window: "Окно",
    card_custom_domains: "Пользовательские домены",
    label_custom_domains: "Домены (по одному в строке)",
    btn_save_custom: "Сохранить",
    about_title: "О BlackKittenproxy",
    about_subtitle: "Десктопный центр управления DPI‑байпасом.",
    about_what_title: "Что делает",
    about_what_body:
      "BlackKittenproxy оборачивает NoDPI в удобную панель. Включайте списки, добавляйте домены и управляйте портом одним кликом.",
    about_lists_title: "Списки + домены",
    about_lists_body:
      "Каждый `.txt` в `unlocked/` становится списком. Выберите нужные, и BlackKittenproxy соберёт новый blacklist.",
    about_design_title: "Дизайн",
    about_design_body:
      "Интерфейс вдохновлён VPN‑панелями вроде AmneziaVPN: атмосферный градиент, сильная типографика, уверенные элементы.",
    rules_title: "Правила",
    rules_subtitle: "Переопределение фрагментации по доменам.",
    rules_list: "Список правил",
    rules_add: "Добавить правило",
    rules_domain: "Домен / Шаблон",
    rules_action: "Действие",
    rules_method: "Метод фрагментации",
    rules_add_btn: "Добавить",
    diag_title: "Диагностика",
    diag_subtitle: "Быстрые проверки прокси и списков.",
    diag_running: "Прокси запущен",
    diag_port: "Порт открыт",
    diag_stats_age: "Возраст статистики",
    diag_blacklist: "Записей в blacklist",
    diag_lists: "Файлы списков",
    diag_actions: "Действия",
    diag_run: "Запустить диагностику",
    logs_title: "Логи",
    logs_subtitle: "Последние access и error логи прокси.",
    logs_controls: "Управление логами",
    logs_access: "Access лог",
    logs_error: "Error лог",
    logs_refresh: "Обновить",
    adv_title: "Расширенные",
    adv_subtitle: "Настройка фрагментации и матчинг режима.",
    adv_mode: "Режим",
    adv_mode_label: "Профиль",
    adv_fragment: "Метод фрагментации",
    adv_fragment_label: "Метод",
    adv_matching: "Сопоставление доменов",
    adv_matching_label: "Режим",
    adv_flags: "Флаги",
    adv_auto_blacklist: "Авто‑blacklist",
    adv_no_blacklist: "Без blacklist (всё подряд)",
    adv_save: "Сохранить",
  },
  es: {
    nav_dashboard: "Panel",
    nav_unlock: "Listas",
    nav_settings: "Ajustes",
    nav_about: "Acerca de",
    nav_rules: "Reglas",
    nav_diagnostics: "Diagnóstico",
    nav_logs: "Registros",
    nav_advanced: "Avanzado",
    subtitle: "Bypass DPI suave con tus listas.",
    card_proxy_status: "Estado del proxy",
    card_active_port: "Puerto activo",
    card_unlocked_lists: "Listas",
    card_enabled_lists: "Habilitadas",
    card_fragment_method: "Método de fragmentación",
    card_sni_strategy: "Estrategia SNI",
    card_connections: "Conexiones",
    card_efficiency: "Eficiencia",
    card_efficiency_meta: "Desbloqueadas / total",
    card_live_speed: "Velocidad",
    card_traffic_graph: "Gráfico de tráfico",
    card_quick_actions: "Acciones rápidas",
    btn_refresh_lists: "Actualizar listas",
    btn_open_unlocked: "Abrir unlocked/",
    btn_open_blacklist: "Abrir GUI blacklist",
    btn_fullscreen: "Pantalla completa",
    btn_compact: "Compacto",
    btn_reset_window: "Restablecer tamaño",
    unlock_title: "Listas de desbloqueo",
    unlock_subtitle: "Cada lista está en `unlocked/` como `.txt`.",
    add_new_website: "Agregar sitio",
    label_list_name: "Nombre de lista",
    label_domains: "Dominios (uno por línea)",
    btn_add_list: "Agregar",
    settings_title: "Ajustes",
    settings_subtitle: "Puertos, idioma y dominios personalizados.",
    card_proxy_network: "Red del proxy",
    label_host: "Host",
    label_port: "Puerto",
    btn_save_network: "Guardar",
    card_language: "Idioma",
    label_language: "Idioma de la interfaz",
    btn_save_language: "Guardar",
    lang_auto: "Auto (sistema)",
    card_window: "Ventana",
    card_custom_domains: "Dominios personalizados",
    label_custom_domains: "Dominios (uno por línea)",
    btn_save_custom: "Guardar",
    about_title: "Acerca de BlackKittenproxy",
    about_subtitle: "Centro de control para tu proxy DPI.",
    about_what_title: "Qué hace",
    about_what_body:
      "BlackKittenproxy envuelve NoDPI con un panel moderno. Activa listas, añade dominios y gestiona el puerto con un clic.",
    about_lists_title: "Listas + dominios",
    about_lists_body:
      "Cada `.txt` en `unlocked/` se convierte en una lista. Activa las que necesites y se genera un blacklist nuevo.",
    about_design_title: "Diseño",
    about_design_body:
      "Inspirado en paneles VPN como AmneziaVPN: gradientes atmosféricos, tipografía fuerte y controles claros.",
    rules_title: "Reglas",
    rules_subtitle: "Anula la fragmentación por dominio.",
    rules_list: "Lista de reglas",
    rules_add: "Agregar regla",
    rules_domain: "Dominio / Patrón",
    rules_action: "Acción",
    rules_method: "Método de fragmentación",
    rules_add_btn: "Agregar",
    diag_title: "Diagnóstico",
    diag_subtitle: "Comprobaciones rápidas del proxy y listas.",
    diag_running: "Proxy en ejecución",
    diag_port: "Puerto abierto",
    diag_stats_age: "Edad de estadísticas",
    diag_blacklist: "Entradas blacklist",
    diag_lists: "Archivos de listas",
    diag_actions: "Acciones",
    diag_run: "Ejecutar diagnóstico",
    logs_title: "Registros",
    logs_subtitle: "Últimos logs de acceso y error.",
    logs_controls: "Controles de logs",
    logs_access: "Log de acceso",
    logs_error: "Log de error",
    logs_refresh: "Actualizar",
    adv_title: "Avanzado",
    adv_subtitle: "Ajusta fragmentación y coincidencia.",
    adv_mode: "Modo",
    adv_mode_label: "Perfil",
    adv_fragment: "Método de fragmentación",
    adv_fragment_label: "Método",
    adv_matching: "Coincidencia de dominios",
    adv_matching_label: "Modo",
    adv_flags: "Flags",
    adv_auto_blacklist: "Auto blacklist",
    adv_no_blacklist: "Sin blacklist (todo)",
    adv_save: "Guardar",
  },
  de: {
    nav_dashboard: "Übersicht",
    nav_unlock: "Listen",
    nav_settings: "Einstellungen",
    nav_about: "Über",
    nav_rules: "Regeln",
    nav_diagnostics: "Diagnose",
    nav_logs: "Logs",
    nav_advanced: "Erweitert",
    subtitle: "Sanfter DPI‑Bypass mit deinen Listen.",
    card_proxy_status: "Proxy‑Status",
    card_active_port: "Aktiver Port",
    card_unlocked_lists: "Listen",
    card_enabled_lists: "Aktiv",
    card_fragment_method: "Fragment‑Methode",
    card_sni_strategy: "SNI‑Strategie",
    card_connections: "Verbindungen",
    card_efficiency: "Effizienz",
    card_efficiency_meta: "Entblockt / gesamt",
    card_live_speed: "Geschwindigkeit",
    card_traffic_graph: "Traffic‑Grafik",
    card_quick_actions: "Schnellaktionen",
    btn_refresh_lists: "Listen aktualisieren",
    btn_open_unlocked: "unlocked/ öffnen",
    btn_open_blacklist: "GUI‑Blacklist öffnen",
    btn_fullscreen: "Vollbild",
    btn_compact: "Kompakt",
    btn_reset_window: "Größe zurücksetzen",
    unlock_title: "Entsperrlisten",
    unlock_subtitle: "Jede Liste liegt in `unlocked/` als `.txt`.",
    add_new_website: "Website hinzufügen",
    label_list_name: "Listenname",
    label_domains: "Domains (eine pro Zeile)",
    btn_add_list: "Hinzufügen",
    settings_title: "Einstellungen",
    settings_subtitle: "Ports, Sprache und benutzerdefinierte Domains.",
    card_proxy_network: "Proxy‑Netzwerk",
    label_host: "Host",
    label_port: "Port",
    btn_save_network: "Speichern",
    card_language: "Sprache",
    label_language: "Sprache der Oberfläche",
    btn_save_language: "Speichern",
    lang_auto: "Auto (System)",
    card_window: "Fenster",
    card_custom_domains: "Eigene Domains",
    label_custom_domains: "Domains (eine pro Zeile)",
    btn_save_custom: "Speichern",
    about_title: "Über BlackKittenproxy",
    about_subtitle: "Desktop‑Kontrollzentrum für deinen DPI‑Proxy.",
    about_what_title: "Was es macht",
    about_what_body:
      "BlackKittenproxy umhüllt NoDPI mit einem modernen Control Center. Listen aktivieren, Domains hinzufügen, Port verwalten.",
    about_lists_title: "Listen + Domains",
    about_lists_body:
      "Jede `.txt` in `unlocked/` ist eine Liste. Aktiviere die gewünschten Listen und BlackKittenproxy baut die Blacklist neu.",
    about_design_title: "Design",
    about_design_body:
      "Inspiriert von VPN‑Dashboards wie AmneziaVPN: atmosphärische Gradients, starke Typografie, klare Controls.",
    rules_title: "Regeln",
    rules_subtitle: "Fragmentierung pro Domain überschreiben.",
    rules_list: "Regelliste",
    rules_add: "Regel hinzufügen",
    rules_domain: "Domain / Muster",
    rules_action: "Aktion",
    rules_method: "Fragment‑Methode",
    rules_add_btn: "Hinzufügen",
    diag_title: "Diagnose",
    diag_subtitle: "Schnelle Checks für Proxy und Listen.",
    diag_running: "Proxy läuft",
    diag_port: "Port offen",
    diag_stats_age: "Statistik‑Alter",
    diag_blacklist: "Blacklist‑Einträge",
    diag_lists: "Listen‑Dateien",
    diag_actions: "Aktionen",
    diag_run: "Diagnose starten",
    logs_title: "Logs",
    logs_subtitle: "Letzte Access- und Error‑Logs.",
    logs_controls: "Log‑Steuerung",
    logs_access: "Access‑Log",
    logs_error: "Error‑Log",
    logs_refresh: "Aktualisieren",
    adv_title: "Erweitert",
    adv_subtitle: "Fragmentierung und Matching feintunen.",
    adv_mode: "Modus",
    adv_mode_label: "Profil",
    adv_fragment: "Fragment‑Methode",
    adv_fragment_label: "Methode",
    adv_matching: "Domain‑Matching",
    adv_matching_label: "Modus",
    adv_flags: "Flags",
    adv_auto_blacklist: "Auto‑Blacklist",
    adv_no_blacklist: "Kein Blacklist (alles)",
    adv_save: "Speichern",
  },
};

const applyTranslations = (lang) => {
  const dict = translations[lang] || translations.en;
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    const key = node.getAttribute("data-i18n");
    if (dict[key]) {
      node.textContent = dict[key];
    }
  });
  const activeNav = document.querySelector(".nav-item.active");
  if (activeNav) {
    document.getElementById("section-title").textContent = activeNav.textContent;
  }
};

const detectLanguage = () => {
  const locale = (navigator.language || "en").toLowerCase();
  const short = locale.split("-")[0];
  return translations[short] ? short : "en";
};

const resolveLanguage = (lang) => {
  if (!lang || lang === "auto") {
    return detectLanguage();
  }
  return translations[lang] ? lang : "en";
};

const apiGet = async (path) => {
  const res = await fetch(path);
  if (!res.ok) {
    throw new Error(await res.text());
  }
  return res.json();
};

const apiPost = async (path, payload) => {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: payload ? JSON.stringify(payload) : null,
  });
  if (!res.ok) {
    throw new Error(await res.text());
  }
  return res.json();
};

const apiDelete = async (path) => {
  const res = await fetch(path, { method: "DELETE" });
  if (!res.ok) {
    throw new Error(await res.text());
  }
  return res.json();
};

const setStatus = (running, meta = "") => {
  const statusText = document.getElementById("status-text");
  const statusMeta = document.getElementById("status-meta");
  const statusPill = document.getElementById("status-pill");
  const badge = document.getElementById("proxy-badge");
  const topToggle = document.getElementById("top-toggle");
  const sideToggle = document.getElementById("toggle-proxy");

  statusText.textContent = running ? "Running" : "Stopped";
  statusMeta.textContent = running ? meta || "Proxy online" : "Not running";
  statusPill.textContent = running ? "Running" : "Stopped";
  badge.textContent = running ? "Online" : "Offline";
  topToggle.textContent = running ? "Stop" : "Start";
  sideToggle.textContent = running ? "Stop Proxy" : "Start Proxy";

  statusPill.classList.toggle("active", running);
  badge.classList.toggle("active", running);
};

const renderLists = () => {
  const grid = document.getElementById("lists-grid");
  grid.innerHTML = "";

  state.lists.forEach((list) => {
    const card = document.createElement("div");
    card.className = "card list-card";

    const title = document.createElement("div");
    title.className = "list-title";
    title.innerHTML = `<span>${list.name}</span>`;

    const toggle = document.createElement("div");
    toggle.className = "toggle" + (list.enabled ? " active" : "");
    toggle.addEventListener("click", async () => {
      await apiPost(`/api/lists/${encodeURIComponent(list.name)}/toggle`, {
        enabled: !list.enabled,
      });
      await refreshLists();
    });

    title.appendChild(toggle);

    const meta = document.createElement("div");
    meta.className = "card-meta";
    meta.textContent = `${list.count} domains`;

    const actions = document.createElement("div");
    actions.className = "list-actions";

    const edit = document.createElement("button");
    edit.className = "ghost";
    edit.textContent = "Edit";

    const remove = document.createElement("button");
    remove.className = "ghost";
    remove.textContent = "Remove";

    const editor = document.createElement("div");
    editor.style.display = "none";
    editor.className = "form";

    const textarea = document.createElement("textarea");
    textarea.rows = 4;
    textarea.value = list.domains.join("\n");

    const save = document.createElement("button");
    save.className = "primary";
    save.textContent = "Save";

    save.addEventListener("click", async () => {
      await apiPost(`/api/lists/${encodeURIComponent(list.name)}`, {
        domains: textarea.value,
      });
      await refreshLists();
      editor.style.display = "none";
    });

    edit.addEventListener("click", () => {
      editor.style.display = editor.style.display === "none" ? "grid" : "none";
    });

    remove.addEventListener("click", async () => {
      await apiDelete(`/api/lists/${encodeURIComponent(list.name)}`);
      await refreshLists();
    });

    editor.appendChild(textarea);
    editor.appendChild(save);

    actions.appendChild(edit);
    actions.appendChild(remove);

    card.appendChild(title);
    card.appendChild(meta);
    card.appendChild(actions);
    card.appendChild(editor);

    grid.appendChild(card);
  });

  document.getElementById("list-count").textContent = state.lists.filter((l) => l.enabled).length;
};

const refreshConfig = async () => {
  state.config = await apiGet("/api/config");
  document.getElementById("port-text").textContent = state.config.port;
  document.getElementById("host-text").textContent = state.config.host;
  document.getElementById("host-input").value = state.config.host;
  document.getElementById("port-input").value = state.config.port;
  document.getElementById("language-select").value = state.config.language || "auto";
  document.getElementById("custom-domains").value = state.config.custom_domains.join("\n");
  document.getElementById("fragment-method").value = state.config.fragment_method || "random";
  document.getElementById("domain-matching").value = state.config.domain_matching || "strict";
  document.getElementById("proxy-mode").value = state.config.mode || "custom";
  document.getElementById("auto-blacklist").checked = !!state.config.auto_blacklist;
  document.getElementById("no-blacklist").checked = !!state.config.no_blacklist;
  state.rules = state.config.rules || [];
  renderRules();
  applyTranslations(resolveLanguage(state.config.language));
};

const refreshLists = async () => {
  state.lists = await apiGet("/api/lists");
  renderLists();
};

const refreshStatus = async () => {
  state.status = await apiGet("/api/status");
  setStatus(state.status.running, state.status.message);
};

const refreshStats = async () => {
  const stats = await apiGet("/api/stats");
  if (!stats || Object.keys(stats).length === 0) {
    return;
  }
  const fragment = document.getElementById("fragment-text");
  const connectionsText = document.getElementById("connections-text");
  const connectionsMeta = document.getElementById("connections-meta");
  const efficiencyText = document.getElementById("efficiency-text");
  const speedText = document.getElementById("speed-text");
  const speedMeta = document.getElementById("speed-meta");

  fragment.textContent = stats.fragment_method || "—";
  connectionsText.textContent = stats.total_connections ?? 0;
  const allowed = stats.allowed_connections ?? 0;
  const blocked = stats.blocked_connections ?? 0;
  const errors = stats.error_connections ?? 0;
  connectionsMeta.textContent = `Allowed ${allowed} · Unblocked ${blocked} · Errors ${errors}`;

  const efficiency = typeof stats.efficiency === "number" ? stats.efficiency : 0;
  efficiencyText.textContent = `${efficiency.toFixed(1)}%`;

  const dl = stats.speed_in_bps ?? 0;
  const ul = stats.speed_out_bps ?? 0;
  speedText.textContent = formatSpeed(dl + ul);
  speedMeta.textContent = `DL ${formatSpeed(dl)} · UL ${formatSpeed(ul)}`;

  state.speedHistory.push({ dl, ul });
  if (state.speedHistory.length > state.maxHistory) {
    state.speedHistory.shift();
  }
  drawGraph();
};

const refreshDiagnostics = async () => {
  const diag = await apiGet("/api/diagnostics");
  document.getElementById("diag-running").textContent = diag.running ? "Yes" : "No";
  document.getElementById("diag-port").textContent = diag.port_open ? "Yes" : "No";
  const age = diag.stats_age_sec;
  document.getElementById("diag-stats-age").textContent = age === null ? "—" : `${age.toFixed(1)}s`;
  document.getElementById("diag-blacklist").textContent = diag.blacklist_entries ?? 0;
  document.getElementById("diag-lists").textContent = diag.list_files ?? 0;
};

const refreshLogs = async () => {
  const output = document.getElementById("logs-output");
  try {
    const data = await apiGet(`/api/logs/${state.logType}?limit=200`);
    output.textContent = (data.lines || []).join("\n");
  } catch (err) {
    output.textContent = "Logs are available only from localhost.";
  }
};

const renderRules = () => {
  const container = document.getElementById("rules-list");
  container.innerHTML = "";
  if (!state.rules.length) {
    container.textContent = "No rules yet.";
    return;
  }
  state.rules.forEach((rule, idx) => {
    const item = document.createElement("div");
    item.className = "rule-item";
    const left = document.createElement("div");
    left.innerHTML = `<strong>${rule.pattern}</strong> <span class="rule-meta">${rule.action}</span>`;
    const right = document.createElement("div");
    const method = rule.fragment_method || "default";
    right.innerHTML = `<span class="rule-meta">${method}</span>`;

    const remove = document.createElement("button");
    remove.className = "ghost";
    remove.textContent = "Remove";
    remove.addEventListener("click", async () => {
      state.rules.splice(idx, 1);
      await apiPost("/api/rules", { rules: state.rules });
      await refreshConfig();
    });

    item.appendChild(left);
    item.appendChild(right);
    item.appendChild(remove);
    container.appendChild(item);
  });
};

const formatSpeed = (bps) => {
  if (!bps || bps <= 0) return "0 b/s";
  const units = ["b/s", "Kb/s", "Mb/s", "Gb/s"];
  let value = bps;
  let idx = 0;
  while (value >= 1000 && idx < units.length - 1) {
    value /= 1000;
    idx += 1;
  }
  return `${value.toFixed(value >= 100 ? 0 : 1)} ${units[idx]}`;
};

const drawGraph = () => {
  const canvas = document.getElementById("traffic-graph");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const width = canvas.width;
  const height = canvas.height;

  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = "rgba(8, 8, 10, 0.4)";
  ctx.fillRect(0, 0, width, height);

  const max = Math.max(
    1,
    ...state.speedHistory.map((p) => Math.max(p.dl, p.ul))
  );

  const step = width / Math.max(1, state.maxHistory - 1);

  const drawLine = (key, color) => {
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.beginPath();
    state.speedHistory.forEach((point, idx) => {
      const value = point[key];
      const x = idx * step;
      const y = height - (value / max) * (height - 20) - 10;
      if (idx === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    ctx.stroke();
  };

  drawLine("dl", "rgba(244, 242, 239, 0.9)");
  drawLine("ul", "rgba(207, 201, 196, 0.85)");
};

const toggleFullscreen = async () => {
  if (window.pywebview && window.pywebview.api && window.pywebview.api.toggle_fullscreen) {
    await window.pywebview.api.toggle_fullscreen();
  }
};

const setCompactWindow = async () => {
  if (window.pywebview && window.pywebview.api && window.pywebview.api.set_window_size) {
    await window.pywebview.api.set_window_size(980, 640);
  }
};

const resetWindow = async () => {
  if (window.pywebview && window.pywebview.api && window.pywebview.api.reset_window) {
    await window.pywebview.api.reset_window();
  }
};

const initNav = () => {
  const buttons = document.querySelectorAll(".nav-item");
  const panels = document.querySelectorAll(".panel");
  const title = document.getElementById("section-title");
  const content = document.querySelector(".content");

  buttons.forEach((btn) => {
    btn.addEventListener("click", async () => {
      buttons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");

      panels.forEach((panel) => panel.classList.remove("active"));
      const target = document.getElementById(btn.dataset.section);
      if (target) {
        target.classList.add("active");
        title.textContent = btn.textContent;
      }
      if (content) {
        content.scrollTop = 0;
      }

      if (btn.dataset.section === "diagnostics") {
        await refreshDiagnostics();
      }
      if (btn.dataset.section === "logs") {
        await refreshLogs();
      }
      if (btn.dataset.section === "rules") {
        renderRules();
      }
    });
  });
};

const bindActions = () => {
  document.getElementById("top-toggle").addEventListener("click", async () => {
    if (state.status?.running) {
      await apiPost("/api/proxy/stop");
    } else {
      await apiPost("/api/proxy/start");
    }
    await refreshStatus();
  });

  document.getElementById("toggle-proxy").addEventListener("click", async () => {
    if (state.status?.running) {
      await apiPost("/api/proxy/stop");
    } else {
      await apiPost("/api/proxy/start");
    }
    await refreshStatus();
  });

  document.getElementById("toggle-fullscreen").addEventListener("click", async () => {
    await toggleFullscreen();
  });

  document.getElementById("compact-window").addEventListener("click", async () => {
    await setCompactWindow();
  });

  document.getElementById("reset-window").addEventListener("click", async () => {
    await resetWindow();
  });

  document.getElementById("refresh-lists").addEventListener("click", async () => {
    await refreshLists();
  });

  document.getElementById("open-unlocked").addEventListener("click", async () => {
    await apiPost("/api/open/unlocked");
  });

  document.getElementById("open-blacklist").addEventListener("click", async () => {
    await apiPost("/api/open/blacklist");
  });

  document.getElementById("add-list").addEventListener("click", async () => {
    const name = document.getElementById("new-list-name").value.trim();
    const domains = document.getElementById("new-list-domains").value.trim();
    const hint = document.getElementById("add-list-hint");
    hint.textContent = "";
    if (!name) {
      hint.textContent = "List name is required.";
      return;
    }
    await apiPost("/api/lists", { name, domains });
    document.getElementById("new-list-name").value = "";
    document.getElementById("new-list-domains").value = "";
    hint.textContent = "Added!";
    await refreshLists();
  });

  document.getElementById("save-network").addEventListener("click", async () => {
    const host = document.getElementById("host-input").value.trim();
    const port = Number(document.getElementById("port-input").value.trim());
    await apiPost("/api/config", { host, port });
    await refreshConfig();
  });

  document.getElementById("save-language").addEventListener("click", async () => {
    const language = document.getElementById("language-select").value;
    await apiPost("/api/config", { language });
    await refreshConfig();
    applyTranslations(resolveLanguage(language));
  });

  document.getElementById("save-custom").addEventListener("click", async () => {
    const domains = document.getElementById("custom-domains").value;
    await apiPost("/api/config", { custom_domains: domains });
    document.getElementById("custom-hint").textContent = "Saved.";
    await refreshConfig();
  });

  document.getElementById("run-diagnostics").addEventListener("click", async () => {
    await refreshDiagnostics();
  });

  document.getElementById("logs-access").addEventListener("click", async () => {
    state.logType = "access";
    await refreshLogs();
  });

  document.getElementById("logs-error").addEventListener("click", async () => {
    state.logType = "error";
    await refreshLogs();
  });

  document.getElementById("logs-refresh").addEventListener("click", async () => {
    await refreshLogs();
  });

  document.getElementById("save-advanced").addEventListener("click", async () => {
    const mode = document.getElementById("proxy-mode").value;
    const fragment_method = document.getElementById("fragment-method").value;
    const domain_matching = document.getElementById("domain-matching").value;
    let auto_blacklist = document.getElementById("auto-blacklist").checked;
    let no_blacklist = document.getElementById("no-blacklist").checked;
    if (no_blacklist) {
      auto_blacklist = false;
    }
    await apiPost("/api/config", {
      mode,
      fragment_method,
      domain_matching,
      auto_blacklist,
      no_blacklist,
    });
    document.getElementById("advanced-hint").textContent = "Saved.";
    await refreshConfig();
  });

  document.getElementById("add-rule").addEventListener("click", async () => {
    const pattern = document.getElementById("rule-domain").value.trim();
    const action = document.getElementById("rule-action").value;
    const fragment_method = document.getElementById("rule-method").value || null;
    if (!pattern) {
      return;
    }
    state.rules.push({ pattern, action, fragment_method });
    await apiPost("/api/rules", { rules: state.rules });
    document.getElementById("rule-domain").value = "";
    document.getElementById("rule-method").value = "";
    await refreshConfig();
  });
};

const init = async () => {
  const overlay = document.getElementById("loading-overlay");
  initNav();
  bindActions();
  try {
    await refreshConfig();
    await refreshLists();
    await refreshStatus();
    await refreshStats();
  } finally {
    overlay.classList.add("hidden");
    setTimeout(() => overlay.remove(), 400);
  }
  setInterval(refreshStats, 1000);
  window.addEventListener("resize", drawGraph);
  window.addEventListener("keydown", async (event) => {
    if (event.key === "F11") {
      event.preventDefault();
      await toggleFullscreen();
    }
  });
};

window.addEventListener("DOMContentLoaded", init);
