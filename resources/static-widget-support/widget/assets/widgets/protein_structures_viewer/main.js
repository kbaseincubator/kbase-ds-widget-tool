export function protein_structures_viewer_main(pdbInfos) {
    // Initialize data table for the compounds table
    new DataTable('#main-table', {
        paging: false,
        scrollCollapse: true,
        scrollY: '400px',
        dom: '<"dataTablesOverride-top"if>t'
    });

    const pdbInfosMap = pdbInfos.reduce((pdbInfosMap, info) => {
        pdbInfosMap[info.structure_name] = info;
        return pdbInfosMap;
    }, {});

    for (const {structure_name} of pdbInfos) {
        $(`#structure_name_${structure_name}`).on('click', () => {
            showMolStarViewer(pdbInfosMap[structure_name]);
        });
    }

    function renderMolstarViewer(id, name) {
        molstar.Viewer.create(id, {
                layoutIsExpanded: false,
                layoutShowControls: false,
                layoutShowRemoteState: false,
                layoutShowSequence: true,
                layoutShowLog: false,
                layoutShowLeftPanel: true,

                viewportShowExpand: true,
                viewportShowSelectionMode: false,
                viewportShowAnimation: false,

                pdbProvider: 'rcsb',
                emdbProvider: 'rcsb',
            }).then(viewer => {
            viewer.loadPdb(name);
            // viewer.loadEmdb('EMD-30210', { detail: 6 });
            });
    }

    /**
     * Adds a tab with a placeholder for content to be rendered into.
     *
     * @param {string} tabsId The base identifier for the tabset;
     * @param {string} id The base identifier for the tab and tab content
     * @param {string} label The tab label
     * @returns {(*|jQuery|string)[]}
     */
    function $addTab(tabsId, id, label) {
        const tabId = `${id}-tab`;
        // const viewerId = `${id}-viewer`;

        // If the tab exists, select it.
        const existingTab = $(`#${tabId}`).get(0);
        if (existingTab) {
            new bootstrap.Tab(existingTab).show();
            return;
        }

        const $tab = $('<li>')
            .addClass('nav-item').attr('role', 'presentation')
            .append(
                $('<div>')
                    .addClass('btn-group')
                    .append(
                        $('<button>')
                            .text(label)
                            .addClass('nav-link')
                            .attr('id', tabId)
                            .attr('data-bs-toggle', 'tab')
                            .attr('data-bs-target', `#${id}`)
                            .attr('type', 'button')
                            .attr('aria-controls', id)
                            .attr('aria-selected', 'false')
                    )
                    .append(
                        $('<button>')
                            .append($('<span>').addClass('bi bi-x'))
                            .addClass('btn btn-sm btn-link')
                            .css('display', 'inline')
                            .css('padding', '0.25rem')
                            .on('click', (ev) => {
                                $pane.remove();
                                $tab.remove();
                                const $tabs = $(`#${tabsId}-tabs > li button.nav-link`);
                                new bootstrap.Tab($tabs.get(0)).show();
                            })
                    )
            );

        const $viewer = $('<div>')
            // .attr('id', viewerId)
            .attr('data-element', 'viewer')
            .css('flex', '1 1 0')
            .css('position', 'relative');

        const $pane =  $('<div>')
            .addClass('tab-pane fade pt-3')
            .attr('id', id)
            .attr('role', 'tabpanel')
            .attr('aria-labelledby', tabId)
            .append($viewer);

        // Note that this relies upon the tabset having ids matching
        // this pattern (which is not required by bootstrap).
        $(`#${tabsId}-tabs`).append($tab);
        $(`#${tabsId}-content`).append($pane);

        new bootstrap.Tab($tab.find('button').get(0)).show();

        return $pane;
    }

    function showMolStarViewer(pdbInfo) {
        // add tab.
        const name = pdbInfo.structure_name;
        const id = `protein-structure-${name}`;
        const tabsId = 'protein-structures';
        const $tabPane = $addTab(tabsId, id, name);

        // Set a unique id with which to associate the pane's content element with the
        // molstar viewer. The molstar viewer requires an id, not an element or selector,
        // in order to render.
        const molstarId = `${id}-molstar`;
        $tabPane.find('[data-element="viewer"]').attr('id', molstarId);
        renderMolstarViewer(molstarId, name);
    }
}