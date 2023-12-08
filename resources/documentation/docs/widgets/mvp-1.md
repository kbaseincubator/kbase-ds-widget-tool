# Minimal Viable Product # 1

The goals of the first release of the Dynamic Service Widget are:

- Be able to implement an object viewer widget in a KBase SDK Dynamic Service (DS) using a
  tool that allows one to apply a set of changes to a stock KBase SDK DS.

- Widgets may be implemented in Python, Javascript, or a combination thereof.

- Widgets may require authentication, ignore authentication, or both.

- Widgets may be implemented independently of the Narrative.

- Widgets will be supported by KBase libraries to utilize KBase services, authentication,
  and configuration.

- Widgets will be run from a generic Narrative widget host supporting any DS Widget -
  that is, the Narrative does not require any changes to support a new DS Widget.

- A widget will be invoked in the Narrative by the output of an app, which will specify
  a DS Widget by identifying it as a DS Widget (widget name) and providing the requisite
  parameters
  
- An object viewer DS will require a Workspace object reference or path, may require
  a sub-object path, and may, if private, require an auth token.

## What is left out

Ultimately the DS widget will support other features, which we are intentionally
excluding from MVP-1. We need to release the product in a timely fashion. It will be
useful on its own, but will also help us get experience for the next version.

Features intentionally excluded include:

- Widget state synchronization

- Support for non-viewer widgets - although this is not a big step from a viewer widget

- Any features which require changes to kb-sdk.

- Formal support for versioned, installable KBase libraries

- Support for usage in static Narratives

