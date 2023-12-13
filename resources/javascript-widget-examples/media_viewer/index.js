async function render({token, ref, workspaceURL, uiOrigin}) {
    // Spinners everywhere!
    ["media_object_info_id", "media_object_info_type", "media_object_info_owner",
     "media_object_info_version", "media_object_info_saved_at", "media_object_info_name",
     "media_object_data_source", "media_object_info_metadata_is_minimal", 
     "media_object_info_metadata_is_defined", "media_object_info_metadata_number_compounds"

    ].map((id) => {
        $(document.getElementById(id)).html($('<div>').addClass('spinner-border spinner-border-sm text-secondary').attr('role', 'status')
                .append($('<span>').addClass('visually-hidden').text('Loading..."')))
    })

    const workspaceClient = new ServiceClient({
        url: workspaceURL,
        module: 'Workspace', 
        timeout: 10000,
        token,
        strict: false
    });

    let response = await workspaceClient.callFunc('get_object_info3', {
        objects: [{ref}],
        includeMetadata: 1
    });
    const mediaObjectInfo = objectInfoToObject(response.infos[0]);

    response = await workspaceClient.callFunc('get_workspace_info', {id: mediaObjectInfo.wsid});
    const mediaObjectWorkspaceInfo = workspaceInfoToObject(response);

    const [mediaObject] = await workspaceClient.callFunc('get_objects', [{ref}]);

    // Render Metadata
    $("#media_object_info_id").text(mediaObjectInfo.ref);
    $("#media_object_info_type").html($uilink(uiOrigin, `spec/type/${mediaObjectInfo.type}`, mediaObjectInfo.type))
    $("#media_object_info_owner").html($uilink(uiOrigin, `people/${mediaObjectWorkspaceInfo.owner}`, mediaObjectWorkspaceInfo.owner))
    $("#media_object_info_version").text(mediaObjectInfo.version);
    $("#media_object_info_saved_at").text(mediaObjectInfo.saveDate);
    $("#media_object_info_name").text(mediaObjectInfo.name);
    $("#media_object_data_source").text(mediaObject.data.source_id);
    $("#media_object_info_metadata_is_minimal").text(getMetadata(mediaObjectInfo, 'Is Minimal', (value) => {
        if (!value) {
            return 'n/a';
        }
        return value === '1' ? 'Yes' : 'No';
    }));
    $("#media_object_info_metadata_is_defined").text(getMetadata(mediaObjectInfo, 'Is Defined', (value) => {
        if (!value) {
            return 'n/a';
        }
        return value === '1' ? 'Yes' : 'No';
    }));
    $("#media_object_info_metadata_number_compounds").text(getMetadata(mediaObjectInfo, 'Number compounds', (value) => {
        if (!value) {
            return 'n/a';
        }
        return value;
    }));

    // Render compounds
    const $tableBody = $('#compounds-table tbody')
    for (const compound of mediaObject.data.mediacompounds) {
        const {id, name, formula, charge, minFlux, maxFlux } = compound;
        const $row = $('<tr>')
            .append($('<td>').text(id))
            .append($('<td>').append($('<img>').addClass('compound-image')
                                               .attr('src', `https://minedatabase.mcs.anl.gov/compound_images/ModelSEED/${id}.png`)
                                               .attr('alt', `Image for compound '${id }'`)
                                               .css('max-width', '50px')
                                               .css('width', '100%')
                                               .on('error', function() {
                                                    console.log('this??', this);
                                                    // $(this).unbind('error').attr('src', '/widgets/media_viewer/broken-image.png')
                                                }))
            )
            .append($('<td>').text(name))
            .append($('<td>').text(formula || 'n/a'))
            .append($('<td>').text(charge || 'n/a'))
            .append($('<td>').text(minFlux))
            .append($('<td>').text(maxFlux))
        $tableBody.append($row);
    }

    //   Initialize data table for the compounds table
    const compoundsTable = new DataTable('#compounds-table', {
        pageLength: 10
        // paging: false,
        // scrollCollapse: true,
        // scrollY: '600px',
        // dom: '<"dataTablesOverride-top"if>t'
    });

        // A little hack to get the header to size correctly, as it is initially
        // sized within the hidden second tab.
    $('button[data-bs-toggle="tab"]').on('shown.bs.tab', (ev) => {
        // this.widgetStateUpdated({
        //     tab: ev.target.id
        // });
        const id = ev.target.id;
        if (id !== 'compounds-tab') {
            return;
        }
        compoundsTable.columns.adjust();
    });
    // }
}

const {ref, token, workspaceURL, uiOrigin} = (() => {
    if (window.parent === window) {
        // Self-hosted for development, so get everything from the browser.
        const url = new URL(window.location.href);

        const ref = url.searchParams.get('ref');
        const token = url.searchParams.get('token');
        const env = url.searchParams.get('env') || 'ci';
        const uiOrigin =  `https://${env}.kbase.us`;

        // TODO: import config from python.

        const workspaceURL = `https://${env}.kbase.us/services/ws`;

        console.log('DEV MODE', ref, token);

        return {ref, token, workspaceURL, uiOrigin};
    } else {
        // In an iframe; For now, we also get everything from the url, but we'll change
        // that soon to simulate the Narrative.

        const url = new URL(window.location.href);

        const ref = url.searchParams.get('ref');

        const token = (() => {
            const authCookie = document.cookie.split(';')
                .map((bite) => {
                    return bite.trim().split('=')
                })
                .filter(([name, _]) => {
                    return ['kbase_session', 'kbase_session_backup'].includes(name)
                });
            if (authCookie.length === 0) {
                return null;
            }
            return authCookie[0][1];
        })();

        // TODO: check the token... or just use it, and if it fails, deal with it.

        // Construct a ui origin based on some assumptions.
        // If the origin is ends with kbase.us, use it.
        // Otherwise, assume local development and use ci.
        const uiOrigin = (() => {
            if (window.location.hostname.endsWith('kbase.us')) {
                return window.location.origin;
            } else {
                return 'https://ci.kbase.us';
            }
        })();

        // Construct a kbase endpoint base url based on the same assumptions as above,
        // except that we use kbase.us for prod.
        const kbaseEndpoint = (() => {
            if (window.location.hostname.endsWith('kbase.us')) {
                if (window.location.hostname.startsWith('narrative.')) {
                    return `${window.location.origin}/services/`;
                } else {
                    return 'https://kbase.us/services/';
                }
            } else {
                return 'https://ci.kbase.us/services/';
            }
        })();

       
        // const env = url.searchParams.get('env') || 'ci';
        // const uiOrigin =  `https://${env}.kbase.us`;

        const workspaceURL = `${kbaseEndpoint}ws`;

        return {ref, token, workspaceURL, uiOrigin};
    }
})();

async function main(props) {
    try {
        await render(props)
        $('#loading').remove();
        $('#widget').removeClass("d-none");
    } catch(ex) {
        console.error('ERROR', ex);
        $('#loading').remove();
        $('#error-message').text(ex.message);
        $('#error').removeClass("d-none");
    }
}

main({ ref, token, workspaceURL, uiOrigin });