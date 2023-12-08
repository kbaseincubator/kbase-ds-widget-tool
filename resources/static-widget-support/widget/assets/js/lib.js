// Narrative Interfacing Support
// TODO: move to separate file.
function findHostElement() {
    if (window.frameElement) {
        return window.frameElement || null;
    } else {
        return document.querySelector('[data-app-host="true"]');
    }
}

function getParamsFromDOM() {
    const hostNode = findHostElement();
    if (!hostNode) {
        console.warn('No data-app-host');
        return null;
    }

    const params = hostNode.getAttribute('data-params');
    if (params === null) {
        console.warn('no data-params')
        return null;
    }
    return JSON.parse(decodeURIComponent(params));
}


// WindowMessage postMessage API
// TODO: move to separate file

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

class WindowChannelInit {
    constructor(params = {}) {
        // The given window upon which we will listen for messages.
        this.window = params.window || window;

        // The host for the window; required for postmessage
        this.host = params.host || this.window.document.location.origin;

        // The channel id. Used to filter all messages received to
        // this channel.
        this.id = params.id || uniqueId();
    }

    makeChannel(partnerId) {
        return new WindowChannel({
            window: this.window,
            host: this.host,
            id: this.id,
            to: partnerId
        });
    }

    getId() {
        return this.id;
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

class WindowChannel {
    constructor({window, host, id, to}) {
        // The given window upon which we will listen for messages.
        this.window = window;

        // The host for the window; required for postMessage
        this.host = host;

        // The channel id. Used to filter all messages received to
        // this channel.
        this.id = id;

        this.partnerId = to;

        this.awaitingResponses = new Map();
        this.waitingListeners = new Map();
        this.listeners = new Map();

        this.lastId = 0;

        this.currentListener = null;
        this.running = false;
        this.stats = {
            sent: 0,
            received: 0,
            ignored: 0
        }
    }

    getId() {
        return this.id;
    }

    getPartnerId() {
        return this.partnerId;
    }

    getStats() {
        return this.stats;
    }

    /**
     * Receives all messages sent via postMessage to the associated window.
     *
     * @param messageEvent - a post message event
     */
    receiveMessage(messageEvent) {
        const message = messageEvent.data;

        // Here we have a series of filters to determine whether this message should be
        // handled by this post message bus.
        // In all cases we issue a warning, and return.

        if (!isSimpleObject(message)) {
            // console.warn('[receiveMessage] ignored message because not simple object', message);
            this.stats.ignored += 1;
            return;
        }

        // TODO: could do more here.
        if (!message.envelope) {
            // console.warn('[receiveMessage] ignored message because no envelope', message);
            this.stats.ignored += 1;
            return;
        }

        // Here we ignore messages intended for another windowChannel object.
        if (message.envelope.to !== this.id) {
            // console.warn('[receiveMessage] ignored message because "to" is not this id', this.id, message);
            this.stats.ignored += 1;
            return;
        }

        // console.warn('[receiveMessage] 2', message);

        this.stats.received += 1;

        // A message sent as a request will have registered a response handler
        // in the awaitingResponses hash, using a generated id as the key.
        // TODO: to to rethink using the message id here. Perhaps somehting like a
        // chain of ids, the root of which is the origination id, which is the one
        // known here when it it is sent; the message "id" should be assigned whenver
        // a message is sent, but a response  message would include the original
        // message in the "chain"...

        // We can also have awaiting responses without an originating request.
        // These are useful for, e.g., a promise which awaits a message to be sent
        // within some window...

        // if a reply, we ...
        if (message.envelope.type === 'reply' && this.awaitingResponses.has(message.envelope.inReplyTo)) {
            const response = this.awaitingResponses.get(message.envelope.inReplyTo);
            this.awaitingResponses.delete(message.envelope.inReplyTo);
            if (response) {
                response.handler(message.envelope.status, message.payload);
            }
            return;
        }

        // and also awaiting by message name. Like a listener, but they are only used
        // once.

        if (this.waitingListeners.has(message.name)) {
            const awaiting = this.waitingListeners.get(message.name);
            this.waitingListeners.delete(message.name);
            awaiting.forEach((listener) => {
                try {
                    listener.callback(message.payload);
                } catch (ex) {
                    if (listener.onError) {
                        listener.onError(ex instanceof Error ? ex : new Error('Unknown'));
                    }
                }
            });
        }

        // Otherwise, permanently registered handlers are found in the listeners for the
        // message name.
        const listeners = this.listeners.get(message.name) || [];
        for (const listener of listeners) {
            switch (message.envelope.type) {
                case 'plain':
                    try {
                        return listener.callback(message.payload);
                    } catch (ex) {
                        if (listener.onError) {
                            listener.onError(ex instanceof Error ? ex : new Error('Unknown'));
                        }
                    }
                    break;
                case 'request':
                    const [ok, err] = (() => {
                        try {
                            return [listener.callback(message.payload), null];
                        } catch (ex) {
                            const message = (() => {
                                if (ex instanceof Error) {
                                    return ex.message;
                                }
                                return 'Unknown';
                            })
                            return [null, {message}];
                        }
                    })();
                    const replyEnvelop = {
                        type: 'reply',
                        from: message.envelope.to,
                        to: message.envelope.from,
                        created: Date.now(),
                        id: uniqueId(),
                        inReplyTo: message.envelope.id,
                        status: ok ? 'ok' : 'error'
                    }
                    const replyMessage = new Message({
                        envelope: replyEnvelop,
                        name: 'reply',
                        payload: ok || err
                    });
                    this.sendMessage(replyMessage);
            }
        }
    }

    listen(listener) {
        if (!this.listeners.has(listener.name)) {
            this.listeners.set(listener.name, []);
        }
        this.listeners.get(listener.name).push(listener);
    }

    on(messageId, callback, onError) {
        this.listen(
            new Listener({
                name: messageId,
                callback,
                onError: (error) => {
                    if (onError) {
                        onError(error);
                    }
                }
            })
        );
    }

    sendMessage(message) {
        if (!this.running) {
            throw new Error('Not running - may not send ')
        }
        this.stats.sent += 1;
        this.window.postMessage(message.toJSON(), this.host);
    }

    send(name, payload) {
        const envelope = {
            type: 'plain',
            from: this.id,
            to: this.partnerId,
            created: Date.now(),
            id: uniqueId()
        };
        const message = new Message({name, payload, envelope});
        this.sendMessage(message);
    }

    sendRequest(message, handler) {
        if (!this.running) {
            throw new Error('Not running - may not send ')
        }
        this.awaitingResponses.set(message.envelope.id, {
            started: new Date(),
            handler
        });
        this.sendMessage(message);
    }

    request(name, payload) {
        return new Promise((resolve, reject) => {
            const envelope = {
                type: 'request',
                from: this.id,
                to: this.partnerId,
                created: Date.now(),
                id: uniqueId()
            };
            const message = new Message({
                name,
                payload,
                envelope
            });
            this.sendRequest(message, (status, response) => {
                if (status === 'ok') {
                    resolve(response);
                } else {
                    // TODO: tighten up the typing!!!
                    reject(new Error(response.message));
                }
            });
        });
    }

    startMonitor() {
        window.setTimeout(() => {
            const now = new Date().getTime();

            // first take care of listeners awaiting a message.
            for (const [id, listeners] of Array.from(this.waitingListeners.entries())) {
                const newListeners = listeners.filter((listener) => {
                    if (listener instanceof WaitingListener) {
                        const elapsed = now - listener.started.getTime();
                        if (elapsed > listener.timeout) {
                            try {
                                if (listener.onError) {
                                    listener.onError(new Error('timout after ' + elapsed));
                                }
                            } catch (ex) {
                                console.error('Error calling error handler', id, ex);
                            }
                            return false;
                        } else {
                            return true;
                        }
                    } else {
                        return true;
                    }
                });
                if (newListeners.length === 0) {
                    this.waitingListeners.delete(id);
                }
            }

            if (this.waitingListeners.size > 0) {
                this.startMonitor();
            }
        }, 100);
    }

    listenOnce(listener) {
        if (!this.waitingListeners.has(listener.name)) {
            this.waitingListeners.set(listener.name, []);
        }
        this.waitingListeners.get(listener.name).push(listener);
        if (listener.timeout) {
            this.startMonitor();
        }
    }

    once(name, timeout, callback, onError) {
        this.listenOnce(
            new WaitingListener({
                name: name,
                callback,
                timeout,
                onError: (error) => {
                    if (onError) {
                        onError(error);
                    }
                }
            })
        );
    }

    when(name, timeout) {
        return new Promise((resolve, reject) => {
            return this.listenOnce(
                new WaitingListener({
                    name: name,
                    timeout: timeout,
                    callback: (payload) => {
                        resolve(payload);
                    },
                    onError: (error) => {
                        reject(error);
                    }
                })
            );
        });
    }

    setPartner(id) {
        this.partnerId = id;
    }

    start() {
        this.currentListener = (message) => {
            this.receiveMessage(message);
        };
        this.window.addEventListener('message', this.currentListener, false);
        this.running = true;
        return this;
    }

    stop() {
        this.running = false;
        if (this.currentListener) {
            this.window.removeEventListener('message', this.currentListener, false);
        }
        return this;
    }
}

console.log('loading WidgetRuntime...')
class WidgetRuntime {
    constructor() {
        const iframeParams = getParamsFromDOM();
        const hostChannelId = iframeParams.hostChannelId;
        const channelId = iframeParams.appChannelId;

        // TODO: remove the need for the init?
        const chan = new WindowChannelInit({id: channelId});
        this.channel = chan.makeChannel(hostChannelId);


        // The 'start' message is sent by the Narrative after receiving the
        // 'ready' message. The start message not only indicates the Narrative is
        // ready to interact with the widget, but may also contain additional information,
        // such as the initial state of the widget.
        this.channel.once('start', 100000, (message) => {
            const widgetStateUpdated = (widgetState) => {
                console.log('widget state updated?', widgetState);
                this.channel.send('widget-state', {widgetState});
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
            //

            // Listen for 'click's on the body, and propagate to the cell.
            document.addEventListener('click', () => {
                this.channel.send('click', {});
            });

            // TODO: restore widget state...

            // const { data : {widgetState}} = message;

            // console.log('START?', message);

            try {
                this.start(message)
            } catch (ex) {
                console.error('Error starting: ', ex);
            }

            this.channel.send('started', {channelId});
        });

        // Note that we wait until the widget resources are fully loaded, because the narrative
        // is also listening for the iframe to be loaded, which is also signaled only when
        // everything is loaded.
        // TODO: is this STILL a race condition? Because who gets the
        document.addEventListener("readystatechange", (ev) => {
            if (document.readyState !== "complete") {
                return;
            }

            // Starts listening and sending messages.
            this.channel.start();

            // Tells the narrative we are ready, and can receive messages from it.
            this.channel.send('ready', {channelId: this.channel.getId()});
        });
    }

    widgetStateUpdated (widgetState) {
        console.log('widget state updated?', widgetState);
        this.channel.send('widget-state', {widgetState});
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
 function $uilink(origin, path, label, type='kbaseui', newWindow=true) {
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
function getMetadata(objectInfo, propName, handler) {
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