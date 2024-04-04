import React from 'react';
import { ToastContainer, toast } from 'react-toastify';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';

import Grid from '@mui/material/Grid';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Button from '@mui/material/Button';
import CssBaseline from '@mui/material/CssBaseline';
import Alert from '@mui/material/Alert';
import Stack from '@mui/material/Stack';
import LinearProgress from '@mui/material/LinearProgress';
import ErrorIcon from '@mui/icons-material/Error';
import { Box } from '@mui/material';


import AutomationState from './components/AutomationState';
import AutomationReport from './components/AutomationReport';
import AutomationReadings from './components/AutomationReadings';
import FeedString from './components/FeedString';

import Wizard from './components/Wizard';
import Logo from './components/Logo';
import EventsTable from './components/EventTable';
import AppMenu from './components/AppMenu';

function withLocation(Component) {
return function LocationComponent(props) {
  const location = useLocation();
  return <Component {...props} location={location} />;
}
}

async function asyncRetry(fn, retriesLeft = 3, interval = 1000) {
  try {
    return await fn;
  } catch (error) {
    if (retriesLeft) {
      await new Promise(r => setTimeout(r, interval));
      return await asyncRetry(fn, retriesLeft - 1, interval);
    }
    throw new Error(error);
  }
}

function parseOperationSite() {
  const domain = window.location.hostname;
  let subdomain = domain.split('.');
  return subdomain[1];
}

class App extends React.PureComponent {

  constructor(props) {
    super(props);

    this.state = {
      loading: true,
      errored: false,
      feedStrings: [],
      events: [],
      automation: undefined,
      automationStartSettings: {},
      requestLoading: false,
      eventSourceFailed: false,
      cloudevent: undefined
    };

    this.url = process.env.NODE_ENV === 'development' ? 'http://127.0.0.1:5000' : window.location.origin;
    this.opsite = process.env.NODE_ENV === 'development' ? 'KOA02' : parseOperationSite();
    document.getElementById('title').innerHTML = this.opsite;

    this.eventSource = undefined;
    this.stateSource = undefined;
    this.erroredTimeout = undefined;
    this.onNewEvent = this.onNewEvent.bind(this);
    this.onNewState = this.onNewState.bind(this);
    this.onStartAutomation = this.onStartAutomation.bind(this);
    this.onEventSourceError = this.onEventSourceError.bind(this);
    this.events = [];

    this.handleRequestData = this.handleRequestData.bind(this);
  }

  async componentDidMount() {
    try {
      await this.initialize();

      this.eventSource = new EventSource(`${this.url}/api/automation/events`);
      this.eventSource.onmessage = this.onNewEvent;
      this.eventSource.onerror = this.onEventSourceError;

      this.stateSource = new EventSource(`${this.url}/api/automation/state`);
      this.stateSource.onmessage = this.onNewState;
      this.stateSource.onerror = this.onEventSourceError;
    } catch (error) {
      console.error(error);
      this.setState({ errored: true }, () => {
        this.erroredTimeout = setTimeout(() => {
          window.location.reload();
        }, 30000);
      });
    }
  }

  componentWillUnmount() {
    if (this.erroredTimeout) {
      clearTimeout(this.erroredTimeout);
    }

    this.eventSource?.close();
    this.stateSource?.close();
  }

  async initialize() {
    const results = await asyncRetry(Promise.all([
      this.fetchFeedStrings(),
      this.fetchState()
    ]));

    const [feedStrings, automation] = results;

    this.setState({ 
      feedStrings: feedStrings,
      automation: automation,
      loading: false
    });
  }

  async fetchFeedStrings() {
    const feedStrings = await fetch(`${this.url}/api/automation/feedstring`)
      .then(response => response.json());
    return feedStrings;
  }

  async fetchState() {
    const automation = await fetch(`${this.url}/api/automation/state`)
      .then(response => response.json());
    return automation;
  }

  onNewEvent(event) {

    try {

      const cloudevent = JSON.parse(event.data);

      const data = {
        ...cloudevent.data,
        timestamp: cloudevent.context.timestamp
      }

      const delay = Date.now() - Date.parse(data.timestamp);
      const messageIsNew = delay >= -1000 && delay < 10000;

      if (messageIsNew && data.event === 'automation_completed') {
        toast.info(`Automation ${data.automation_id} completed`);
      }

      if (messageIsNew && data.event === 'acknowledged') {
        toast.info(`Automation ${data.automation_id} acknowledged`);
      }

      if (messageIsNew && data.event === 'automation_paused') {
        toast.info(`Automation ${data.automation_id} was paused`);
      }

      if (messageIsNew && data.event === 'automation_resumed') {
        toast.info(`Automation ${data.automation_id} was resumed`);
      }

      // automation_resume_failed
      // automation_pause_failed
      // automation_reset_failed

      if (messageIsNew && data.event === 'automation_updated') {
        toast.info(`Automation ${data.automation_id} was updated`);
      }

      if (messageIsNew && data.event === 'automation_failed') {
        toast.error(`Automation ${data.automation_id} failed`);
      }

      this.events.unshift(cloudevent);

      if (this.events.length > 200) {
        this.events.pop();
      }

      this.setState({ events: [...this.events], eventSourceFailed: false });
    } catch (error) {
      // do nothing
    }
  }

  onEventSourceError(error) {
    console.error('event source failed', error);
    this.setState({ eventSourceFailed: true });
  }

  onNewState(event) {
    try{
      const cloudevent = JSON.parse(event.data);

      const data = {
        ...cloudevent.data,
        timestamp: cloudevent.context.timestamp
      }
  
      this.setState({ automation: data, eventSourceFailed: false, cloudevent: cloudevent });
    } catch (error) {
      //
    }
  }


  onStartAutomation() {
    if (!this.state.requestLoading) {
      this.setState({ requestLoading: true }, () => {
        fetch(`${this.url}/api/automation/start`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.state.automationStartSettings)
        }).then(response => {
          if (response.status === 202) {
            toast.success('Automation acknowledged to start');
          } else {
            toast.error('Automation failed to start');
          }
        }).finally(() => {
          this.setState({ requestLoading: false });
        });
      });
    }
  }


  handleRequestData(data) {
    this.setState({ automationStartSettings: data }, function () {
      this.onStartAutomation();
    })
  } 

  renderAppBar() {
    return (
      <>
        <Box sx={{ display: 'flex' }}>
            <CssBaseline />
            <AppBar sx={{ boxShadow: 'none', zIndex: (theme) => theme.zIndex.drawer + 1, backgroundColor: '#e3e5e8', color: 'black' }}>
              <Toolbar
                variant="dense"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  backgroundColor: '#e3e5e8',
                }}
              >
                <div className='appbar'>
                  <Logo />
                  <div className='appbar__header'>
                  {this.opsite} AQUAFEED
                  </div>
                </div>
                <AppMenu />
              </Toolbar>
            </AppBar>
          </Box>
          <Toolbar variant="dense" />
        </>
    );
  }

  renderPhaseComponent() {

    const { automation, feedStrings } = this.state;
  
    switch (automation?.phase) {
      case 'ready':
        return <Wizard feedStrings={feedStrings} handler={this.handleRequestData} />;
      case 'preflight':
      case 'setup':
      case 'main':
      case 'teardown':
        return <AutomationState automation={automation} />;
      case 'completed':
        return <AutomationReport automation={automation} />
      default:
        return (
          <Stack sx={{ width: '100%', marginBottom: 2 }} spacing={2}>
              <Alert severity="error">
                Automation State needs to be reset
              </Alert>
          </Stack>
        );
    }
  }

  renderDisclaimers() {
    const { eventSourceFailed, automation } = this.state;

    if (!eventSourceFailed && !automation?.epo) {
      return <></>
    }

    return (
      <Stack sx={{ width: '100%', marginBottom: 2 }} spacing={2}>
        {automation?.epo === true && (
          <Alert severity="error" variant="filled">
            EPO ACTIVE
          </Alert>
        )}
        {eventSourceFailed && (
          <Alert severity="error">
            Disconnected. Please wait while we reconnect you.
          </Alert>
        )}
      </Stack>
    );
  }

  renderErrored() {
    return (
      <div className='errored'>
        <div className='errored__text'>
          <ErrorIcon sx={{ fontSize: 80 }}/>
          {this.opsite} aquafeed has encountered an error.
          <div className='errored__text--small'>
            Please refresh this page to try again.
          </div>
          <Button 
            variant="contained"
            onClick={() => window.location.reload()}
          >
              Reload
          </Button>
        </div>
      </div>
    );
  }

  renderLoading() {
    return (
      <div className='loading'>      
        <div className='loading__text'>
          <LinearProgress size={200} thickness={15} sx={{width: '100%', height: 7, borderRadius: 2}}/>
          <p>LOADING {this.opsite} FEED AUTOMATION</p>
        </div>
      </div>
    );
  }

  renderAppBody() {
    const { events, feedStrings, cloudevent } = this.state;

    return (
      <Routes>
        <Route path="/specs" element={
          <FeedString feedStrings={feedStrings} />
        }></Route>
        <Route path="/" element={
          <Grid container rowSpacing={2} columnSpacing={{ xs: 1, sm: 1, md: 2 }}>
            <Grid item xs={12} sm={12} md={12} className="body__automation">
              {this.renderPhaseComponent()}
            </Grid>
            {/* <Grid item xs={12} sm={12} md={12}>
              <EventsTable events={events} />
            </Grid> */}
          </Grid>
        }>
        </Route>
        <Route path="/advanced" element={
          <Grid container rowSpacing={2} columnSpacing={{ xs: 1, sm: 1, md: 2 }}>
            <Grid item xs={12} sm={12} md={12} className="body__automation">
              {this.renderPhaseComponent()}
            </Grid>
            <Grid item xs={12} sm={12} md={12}>
              <AutomationReadings cloudevent={cloudevent} />
            </Grid>
            <Grid item xs={12} sm={12} md={12}>
              <EventsTable events={events} />
            </Grid>
          </Grid>
        }></Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    );
  }

  render() {
    const { loading, errored } = this.state;

    if (errored) {
      return this.renderErrored();
    }

    if (loading) {
      return this.renderLoading();
    }

    return (
      <>
        {this.renderAppBar()}
        <div className="body">
          {this.renderDisclaimers()}
          {this.renderAppBody()}
        </div>
        <ToastContainer />
      </>
    );
  }
}

export default withLocation(App);