(function () {
    'use strict';

    function initSidebarToggle() {
        if (!document.body.classList.contains('layout-leve')) {
            return;
        }

        var sidebar = document.getElementById('nav-sidebar');
        if (!sidebar) {
            return;
        }

        var toggle = document.createElement('button');
        toggle.type = 'button';
        toggle.className = 'layout-leve__sidebar-toggle';
        toggle.innerHTML = '<span class="icon">☰</span><span class="label">Menu</span>';
        toggle.setAttribute('aria-label', 'Alternar menu lateral');
        toggle.setAttribute('aria-expanded', 'true');

        var collapsedClass = 'layout-leve--sidebar-collapsed';
        var savedState = null;

        try {
            savedState = window.localStorage.getItem('layoutLeveSidebarCollapsed');
        } catch (err) {
            savedState = null;
        }

        if (savedState === '1') {
            document.body.classList.add(collapsedClass);
            toggle.setAttribute('aria-expanded', 'false');
        }

        toggle.addEventListener('click', function () {
            var isCollapsed = document.body.classList.toggle(collapsedClass);
            toggle.setAttribute('aria-expanded', (!isCollapsed).toString());
            try {
                window.localStorage.setItem('layoutLeveSidebarCollapsed', isCollapsed ? '1' : '0');
            } catch (err) {
                /* ignore persistence errors */
            }
        });

        sidebar.parentNode.insertBefore(toggle, sidebar);
    }

    document.addEventListener('DOMContentLoaded', initSidebarToggle);
})();
