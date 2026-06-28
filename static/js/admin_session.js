(function () {
    var adminPrefix = "/admin/";

    if (!window.location.pathname.startsWith(adminPrefix)) {
        return;
    }

    // После «Назад» / bfcache — принудительный запрос к серверу (актуальная история действий).
    window.addEventListener("pageshow", function (event) {
        if (event.persisted) {
            window.location.replace(window.location.href);
        }
    });

    // После очистки истории — не даём браузеру показать старый снимок страницы.
    document.addEventListener("DOMContentLoaded", function () {
        var clearForm = document.querySelector(".clear-log-form");
        if (!clearForm) {
            return;
        }
        clearForm.addEventListener("submit", function () {
            try {
                sessionStorage.setItem("adminLogClearedAt", String(Date.now()));
            } catch (e) {
                /* ignore */
            }
        });

        try {
            var clearedAt = sessionStorage.getItem("adminLogClearedAt");
            if (clearedAt && Date.now() - Number(clearedAt) < 15000) {
                sessionStorage.removeItem("adminLogClearedAt");
                if (window.location.pathname === adminPrefix || window.location.pathname === adminPrefix.slice(0, -1)) {
                    window.location.replace(window.location.href);
                }
            }
        } catch (e) {
            /* ignore */
        }
    });
})();
