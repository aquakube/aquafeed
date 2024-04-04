import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { ExpandMore as ExpandMoreIcon } from '@mui/icons-material';
import SettingsIcon from '@mui/icons-material/Settings';
import FormControl from '@mui/material/FormControl';
import Grid from '@mui/material/Grid';
import FormHelperText from '@mui/material/FormHelperText';
import InputLabel from '@mui/material/InputLabel';
import OutlinedInput from '@mui/material/OutlinedInput';
import InputAdornment from '@mui/material/InputAdornment';
import { toast } from 'react-toastify';
import {
  Button,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Typography,
  SvgIcon,
  Alert,
  LinearProgress,
  Slider
} from '@mui/material';

const FeedConfigurationAccordion = (props) => {

  // const url = process.env.NODE_ENV === 'development' ? 'http://127.0.0.1:5000' : window.env.API_URL;
  const url = process.env.NODE_ENV === 'development' ? 'http://127.0.0.1:5000' : window.location.origin;

  const [expanded, setExpanded] = useState(false);
  const [feedLimit, setFeedLimit] = useState(props.feedLimit);
  const [feedRate, setFeedRate] = useState(props.feedRate);
  const [updateLoading, setUpdateLoading] = useState(false);
  const [isDirty, setIsDirty] = useState(false); // Track if any changes have been made
  const [showCountdown, setShowCountdown] = useState(false);
  const [countdownValue, setCountdownValue] = useState(30);

  const minFeedLimit = props.feedString.hopper.settings.feedAmount.min;
  const maxFeedLimit = props.feedString.hopper.settings.feedAmount.max;
  const minFeedRate = props.feedString.augers.reduce((total, auger) => total + auger.settings.feedRate.min, 0);
  const maxFeedRate = props.feedString.augers.reduce((total, auger) => total + auger.settings.feedRate.max, 0);

  useEffect(() => {
    // Check if any changes have been made when feedLimit or feedRate updates
    if (props.feedLimit !== feedLimit || props.feedRate !== feedRate) {
      setIsDirty(true);
    } else {
      setIsDirty(false);
    }
  }, [props.feedLimit, props.feedRate, feedLimit, feedRate]);

  useEffect(() => {
    if (props.feedDelivered >= props.feedLimit) {
      setExpanded(true);
      setShowCountdown(true);
      setCountdownValue(30);
    } else {
      setShowCountdown(false);
    }
  }, [props.feedDelivered, props.feedLimit]);

  useEffect(() => {
    let countdownInterval;

    if (showCountdown) {
      countdownInterval = setInterval(() => {
        setCountdownValue((prevValue) => prevValue - 1);
      }, 1000);
    }

    return () => {
      clearInterval(countdownInterval);
    };
  }, [showCountdown]);

  useEffect(() => {
    if (countdownValue <= 0) {
      // Handle what to do when the countdown reaches 0 (e.g., entering teardown phase)
      // You can add your custom logic here or display a message, etc.
      setShowCountdown(false);
    }
  }, [countdownValue]);

  const onUpdateAutomation = () => {
    if (!updateLoading) {
      setUpdateLoading(true);
      fetch(`${url}/api/automation/update`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          feed_limit: feedLimit,
          feed_rate: feedRate,
          time_limit: props.timeLimit,
          plc_readings: [],
        }),
      })
        .then((response) => {
          if (response.status === 202) {
            toast.success('Automation acknowledged update');
          } else {
            toast.error('Automation failed to update');
          }
        })
        .finally(() => {
          setUpdateLoading(false);
        });
    }
  };

  const handleAccordionChange = (event, isExpanded) => {
    setExpanded(isExpanded);
  };

  return (
    <Accordion expanded={expanded} onChange={handleAccordionChange}>
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <SvgIcon>
          <SettingsIcon />
        </SvgIcon>
        <Typography>Configuration</Typography>
      </AccordionSummary>
      <AccordionDetails>
        <Grid container rowSpacing={2} columnSpacing={{ xs: 1, sm: 1, md: 2 }}>

          {showCountdown && (
            <Grid item xs={12} sm={12} md={12}>
              <Alert severity="warning">
                The {props.feedDelivered.toFixed(2)} kg feed has completed.
                Update the automation within {countdownValue} seconds or the system will enter teardown phase!
              </Alert>
              {/* <LinearProgress value={(30 - countdownValue) * (100 / 30)} variant="determinate" color="warning" /> */}
              <LinearProgress value={(countdownValue / 30) * 100 } variant="determinate" color="warning" />
            </Grid>
          )}

          <Grid item xs={12} sm={6} md={6}>
            <FormControl fullWidth variant="outlined">
              <InputLabel htmlFor="outlined-adornment-feed-limit">Feed Amount</InputLabel>
              <OutlinedInput
                id="outlined-adornment-feed-limit"
                error={feedLimit < minFeedLimit || feedLimit > maxFeedLimit}
                label="Feed Limit"
                type="number"
                value={feedLimit}
                onChange={(e) => setFeedLimit(Number(e.target.value))}
                endAdornment={<InputAdornment position="end">kg</InputAdornment>}
                inputProps={{
                  min: minFeedLimit,
                  max: maxFeedLimit,
                }}
              />
              <FormHelperText
                id="outlined-adornment-feed-limit"
                error
                hidden={feedLimit >= minFeedLimit && feedLimit <= maxFeedLimit}
              >
                Must be between {minFeedLimit}kg and {maxFeedLimit}kg
              </FormHelperText>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={6} md={6}>
            <FormControl fullWidth variant="outlined">
              <InputLabel htmlFor="outlined-adornment-feed-rate">Feed Rate</InputLabel>
              <OutlinedInput
                id="outlined-adornment-feed-rate"
                error={feedRate < minFeedRate || feedRate > maxFeedRate}
                label="Feed Rate"
                type="number"
                value={feedRate}
                onChange={(e) => setFeedRate(Number(e.target.value))}
                endAdornment={<InputAdornment position="end">kg/min</InputAdornment>}
                inputProps={{
                  min: minFeedRate,
                  max: maxFeedRate,
                }}
              />
              <FormHelperText
                id="outlined-adornment-feed-rate"
                error
                hidden={feedRate >= minFeedRate && feedRate <= maxFeedRate}
              >
                Feed Rate must be between {minFeedRate} KG/M and {maxFeedRate} KG/M
              </FormHelperText>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={6} md={6}>
            <Slider
              size="small"
              min={minFeedLimit}
              max={maxFeedLimit}
              aria-label="Feed Limit"
              value={feedLimit}
              onChange={(e, value) => setFeedLimit(value)}
            />
          </Grid>
          
          <Grid item xs={12} sm={6} md={6}>
            <Slider
              size="small"
              min={minFeedRate}
              max={maxFeedRate}
              // marks={true}
              aria-label="Feed Rate"
              value={feedRate}
              onChange={(e, value) => setFeedRate(value)}
            />
          </Grid>

          <Grid item xs={12} sm={12} md={12} sx={{ paddingTop: '0px !important' }}>
            <Button
              fullWidth
              onClick={onUpdateAutomation}
              variant="contained"
              color="primary"
              disabled={!isDirty || updateLoading || feedRate < minFeedRate || feedRate > maxFeedRate || feedLimit < minFeedLimit || feedLimit > maxFeedLimit}
            >
              {updateLoading ? 'Updating...' : 'Update'}
            </Button>
          </Grid>
        </Grid>
      </AccordionDetails>
    </Accordion>
  );
};

export default FeedConfigurationAccordion;

FeedConfigurationAccordion.propTypes = {
  feedLimit: PropTypes.number.isRequired,
  feedRate: PropTypes.number.isRequired,
  timeLimit: PropTypes.number.isRequired,
  feedDelivered: PropTypes.number.isRequired,
  feedString: PropTypes.object.isRequired
};
