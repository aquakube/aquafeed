import React, { useState } from 'react';
import PropTypes from 'prop-types';
import PauseIcon from '@mui/icons-material/Pause';
import StopIcon from '@mui/icons-material/Stop';
import PowerSettingsNewIcon from '@mui/icons-material/PowerSettingsNew';
import RestartAltIcon from '@mui/icons-material/RestartAlt';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { Button, Card, CardContent, Stack } from '@mui/material';
import { toast } from 'react-toastify';

export const AutomationControlBar = (props) => {
  var { sx, phase, paused, epo } = props;

  // const url = process.env.NODE_ENV === 'development' ? 'http://127.0.0.1:5000' : window.env.API_URL;
  const url = process.env.NODE_ENV === 'development' ? 'http://127.0.0.1:5000' : window.location.origin;

  // State for loading state of each button
  const [pauseLoading, setPauseLoading] = useState(false);
  const [stopLoading, setStopLoading] = useState(false);
  const [epoLoading, setEpoLoading] = useState(false);
  const [clearEpoLoading, setClearEpoLoading] = useState(false);
  const [resetLoading, setResetLoading] = useState(false);
  const [resumeLoading, setResumeLoading] = useState(false);

  const onPauseAutomation = () => {
    if (!pauseLoading) {
      setPauseLoading(true);
      fetch(`${url}/api/automation/pause`, {
        method: 'PUT',
      })
        .then((response) => {
          if (response.status === 202) {
            toast.success('Automation acknowledged to pause');
            // props.paused = true;
          } else {
            toast.error('Automation failed to pause');
          }
        })
        .finally(() => {
          setPauseLoading(false);
        });
    }
  };

  const onStopAutomation = () => {
    if (!stopLoading) {
      setStopLoading(true);
      fetch(`${url}/api/automation/stop`, {
        method: 'PUT',
      })
        .then((response) => {
          if (response.status === 202) {
            toast.success('Automation acknowledged to stop');
          } else {
            toast.error('Automation failed to stop');
          }
        })
        .finally(() => {
          setStopLoading(false);
        });
    }
  };

  const onEPO = () => {
    if (!epoLoading) {
      setEpoLoading(true);
      fetch(`${url}/api/automation/epo/on`, {
        method: 'PUT',
      })
        .then((response) => {
          if (response.status === 202) {
            toast.success('Automation acknowledged emergency power off');
          } else {
            toast.error('Automation failed to emergency power off');
          }
        })
        .finally(() => {
          setEpoLoading(false);
        });
    }
  };

  const onClearEPO = () => {
    if (!clearEpoLoading) {
      setClearEpoLoading(true);
      fetch(`${url}/api/automation/epo/off`, {
        method: 'DELETE',
      })
        .then((response) => {
          if (response.status === 202) {
            toast.success('Automation acknowledged emergency power off');
          } else {
            toast.error('Automation failed to emergency power off');
          }
        })
        .finally(() => {
          setClearEpoLoading(false);
        });
    }
  };


  const onReset = () => {
    if (!resetLoading) {
      setResetLoading(true);
      fetch(`${url}/api/automation/reset`, {
        method: 'PUT',
      })
        .then((response) => {
          if (response.status === 200) {
            toast.success('Automation acknowledge to reset');
          } else {
            toast.error('Automation failed to reset');
          }
        })
        .finally(() => {
          setResetLoading(false);
        });
    }
  };

  const onResumeAutomation = () => {
    if (!resumeLoading) {
      setResumeLoading(true);
      fetch(`${url}/api/automation/resume`, {
        method: 'PUT',
      })
        .then((response) => {
          if (response.status === 202) {
            toast.success('Automation acknowledge to resume');
            // props.paused = false;
          } else {
            toast.error('Automation failed to resume');
          }
        })
        .finally(() => {
          setResumeLoading(false);
        });
    }
  };

  return (
    <Card sx={sx}>
      <CardContent>
        <Stack alignItems="flex-start" direction="row" justifyContent="space-between" spacing={2}>
          {phase === "main" && !paused && (
            <>
              <Button
                fullWidth
                onClick={onPauseAutomation}
                variant="outlined"
                startIcon={<PauseIcon />}
                color="warning"
                disabled={pauseLoading}
              >
                {pauseLoading ? 'Pausing...' : 'Pause'}
              </Button>
            </>
          )}
          {phase === "main" && paused && (
            <>
              <Button
                fullWidth
                onClick={onResumeAutomation}
                variant="outlined"
                startIcon={<PlayArrowIcon />}
                color="success"
                disabled={resumeLoading}
              >
                {resumeLoading ? 'Resuming...' : 'Resume'}
              </Button>
            </>
          )}
          {['main', 'preflight', 'setup'].includes(phase) && (
            <Button
              fullWidth
              onClick={onStopAutomation}
              variant="outlined"
              startIcon={<StopIcon />}
              color="error"
              disabled={stopLoading}
            >
              {stopLoading ? 'Stopping...' : 'Stop'}
            </Button>
          )}
          
          { epo === false && (
            <>
              <Button
                fullWidth
                onClick={onEPO}
                variant="contained"
                startIcon={<PowerSettingsNewIcon />}
                color="error"
                disabled={epoLoading}
              >
                {epoLoading ? 'EMERGENCY POWER OFF...' : 'EMERGENCY POWER OFF'}
              </Button>
            </>
          )}

          { epo === true && (
            <>
              <Button
                fullWidth
                onClick={onClearEPO}
                variant="contained"
                startIcon={<PowerSettingsNewIcon />}
                color="error"
                disabled={clearEpoLoading}
              >
                {clearEpoLoading ? 'Clearing EMERGENCY POWER OFF...' : 'Clear EMERGENCY POWER OFF'}
              </Button>
            </>
          )}

          {['completed'].includes(phase) && (
            <Button
              fullWidth
              onClick={onReset}
              variant="outlined"
              startIcon={<RestartAltIcon />}
              color="success"
              disabled={resetLoading}
            >
              {resetLoading ? 'Resetting...' : 'Reset'}
            </Button>
          )}
        
        </Stack>
      </CardContent>
    </Card>
  );
};

AutomationControlBar.propTypes = {
  sx: PropTypes.object,
  color: PropTypes.string,
  phase: PropTypes.oneOf(['main', 'preflight', 'setup', 'teardown', 'completed']).isRequired,
  paused: PropTypes.bool.isRequired,
  epo: PropTypes.bool.isRequired,
};

AutomationControlBar.defaultProps = {
  color: 'primary',
};
