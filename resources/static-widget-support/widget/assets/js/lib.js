import ReceiveChannel from './ReceiveChannel.js';
import SendChannel from './SendChannel.js';

/**
 * This technique works for cross-origin requests as well.
 * 
 * Not as "secure" or obscured as the iframe-params approach, but does work in all cases.
 * 
 * The iframe params are passed in a JSON-encoded parameter named "iframeParams", which
 * is reserved for this use.
 */
function getParamsFromURL() {
    const iframeParams = new URL(window.location.href).searchParams.get('iframeParams');
    if (!iframeParams) {
        throw new Error('Cannot get "iframeParams" from url!')
    }
    return JSON.parse(iframeParams);
}


function uniqueId() {
    if (window.crypto) {
        return window.crypto.randomUUID();
    } else {
        return `${Date.now()}-${Math.random()}`;
    }
}

class Message {
    constructor({name, payload, envelope}) {
        this.name = name;
        this.payload = payload;
        this.id = uniqueId();
        this.created = new Date();
        this.envelope = envelope;
    }

    toJSON() {
        return {
            envelope: this.envelope,
            name: this.name,
            payload: this.payload
        };
    }
}

// TODO: I think we have a better version of this...
function isSimpleObject(value) {
    if (typeof value !== 'object') {
        return false;
    }
    if (value === null) {
        return false;
    }
    return (value.constructor === {}.constructor);
}

class Listener {
    constructor({name, callback, onError}) {
        this.name = name;
        this.callback = callback;
        this.onError = onError;
    }
}

class WaitingListener extends Listener {
    constructor(params) {
        super(params);
        this.started = new Date();
        this.timeout = params.timeout || 5000;
    }
}

class KBResizeObserver {
    constructor(
        el,
        bufferInterval,
        onResize
    ) {
        this.observedElement = el;
        this.bufferInterval = bufferInterval;
        this.onResize = onResize;

        this.resizeObserver = new window.ResizeObserver(this.onResized.bind(this));

        const { width, height } = this.outerDimensions();
        this.width = width;
        this.height = height;

        this.bufferTimer = null;
        this.resizes = 0;
        this.resizeObserver.observe(this.observedElement);
    }

    outerDimensions() {
        const rect = this.observedElement.getBoundingClientRect();
        const width = Math.ceil(rect.right - rect.left);
        const height = Math.ceil(rect.bottom - rect.top);
        return {
            width,
            height,
        };
    }

    onResized(entries, observer) {
        const { width, height } = this.outerDimensions();
        this.width = width;
        this.height = height;
        this.resizes += 1;
        if (this.bufferTimer) {
            return;
        }
        this.bufferTimer = window.setTimeout(this.resizeTriggered.bind(this), this.bufferInterval);
    }

    resizeTriggered() {
        this.bufferTimer = null;
        this.onResize(this.width, this.height);
        this.resizes = 0;
    }

    done() {
        this.resizeObserver.unobserve(this.observedElement);
    }

    // observe(el: Element) {

    // }

    // unobserve(el: Element) {

    // }
}

export class WidgetRuntime {
    constructor() {
        const iframeParams = getParamsFromURL();
        const {channelId, hostOrigin} = iframeParams;
        this.sendChannel = new SendChannel({
            window: window.parent,
            targetOrigin: hostOrigin,
            // id: appChannelId,
            channel: channelId
        });

        this.receiveChannel = new ReceiveChannel({
            window,
            channel: channelId
        });
        // this.receiveChannel.receiveFrom(hostChannelId);


        // The 'start' message is sent by the Narrative after receiving the
        // 'ready' message. The start message not only indicates the Narrative is
        // ready to interact with the widget, but may also contain additional information,
        // such as the initial state of the widget.
        this.receiveChannel.once('start', 100000, (message) => {
            const widgetStateUpdated = (widgetState) => {
                this.sendChannel.send('widget-state', {widgetState});
            };

            // this.setState({
            //     narrativeContextState: {
            //         status: AsyncProcessStatus.SUCCESS,
            //         value: { message, channel, widgetStateUpdated },
            //     },
            // });

            // this.resizeObserver = new KBResizeObserver(
            //     window.document.body,
            //     100,
            //     (width, height) => {
            //         channel.send('resized', { width, height });
            //     }
            // );

            // Listen for 'click's on the body, and propagate to the cell.
            document.addEventListener('click', () => {
                this.sendChannel.send('click', {});
            });

            // TODO: restore widget state...

            // const { data : {widgetState}} = message;

            try {
                if (this.start) {
                    this.start(message)
                }
            } catch (ex) {
                console.error('Error starting: ', ex);
            }

            const {width, height} = this.outerDimensions(document.body);

            this.sendChannel.send('started', {channelId, height});
        });

        // Note that we wait until the widget resources are fully loaded, because the narrative
        // is also listening for the iframe to be loaded, which is also signaled only when
        // everything is loaded.
        // TODO: is this STILL a race condition? Because who gets the
        if (document.readyState === "complete") {
            this.onReady();
        } else {
            document.addEventListener("readystatechange", (ev) => {
                if (document.readyState !== "complete") {
                    return;
                }
            this.onReady()
            });
        }
    }

    outerDimensions(observedElement) {
        const rect = observedElement.getBoundingClientRect();
        const width = Math.ceil(rect.right - rect.left);
        const height = Math.ceil(rect.bottom - rect.top);
        return {
            width,
            height,
        };
    }

    onReady() {
        this.receiveChannel.start();

        // Tells the narrative we are ready, and can receive messages from it.
        this.sendChannel.send('ready', {});
    }

    widgetStateUpdated (widgetState) {
        this.sendChannel.send('widget-state', {widgetState});
    }

    start() {
        // does nothing by default; override for post-start behavior.
    }
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
        )

    const $viewer = $('<div>')
        // .attr('id', viewerId)
        .attr('data-element', 'viewer')
        .css('flex', '1 1 0')
        .css('position', 'relative')

    const $pane =  $('<div>')
        .addClass('tab-pane fade pt-3')
        .attr('id', id)
        .attr('role', 'tabpanel')
        .attr('aria-labelledby', tabId)
        .append($viewer)

    // Note that this relies upon the tabset having ids matching
    // this pattern (which is not required by bootstrap).
    $(`#${tabsId}-tabs`).append($tab)
    $(`#${tabsId}-content`).append($pane)

    new bootstrap.Tab($tab.find('button').get(0)).show();

    return $pane
}

 // Cheap hack, no cookie yet, no params yet...
export  function $uilink(origin, path, label, type='kbaseui', newWindow=true) {
    const url = new URL(origin);
    switch (type) {
        case 'kbaseui':
            url.hash = `#${path}`;
            break;
        case 'europa':
            url.pathname = path;
    }
    
    const $link = $('<a>').attr('href', url.toString()).text(label);
    if (newWindow) {
        $link.attr('target', '_blank');
    }
    return $link;
    
}
export function getMetadata(objectInfo, propName, handler) {
    let value;
    if (!objectInfo.metadata) {
        value = undefined;
    } else {
        value = objectInfo.metadata[propName];
    }
    try {
        return handler(value);
    } catch (ex) {
        return ex.message;
    }
}