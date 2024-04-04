import React from 'react';
import { Typography } from '@mui/material';
import Grid from '@mui/material/Grid';

import { PhaseProgress } from './PhaseProgress';
import { AutomationFeedElapsedTime } from './AutomationFeedElapsedTime';
import { AutomationControlBar } from './AutomationControlBar';

// Additional components for 'main' phase
import { AutomationFeedRate } from './AutomationFeedRate';
import { AutomationFeedProgress } from './AutomationFeedProgress';
import FeedConfigurationAccordion from './FeedConfigurationAccordion';

function AutomationState(props) {
  const { automation } = props;

  if (!automation || !automation.automation_id) {
    return (
      <>
        <Typography variant="body1">Automation is not running</Typography>
      </>
    );
  }

  const renderMainPhaseComponents = () => (
    <>
      <Grid item xs={12} sm={3} md={3}>
        <AutomationFeedElapsedTime
          sx={{ height: '100%' }}
          phaseElapsedTime={automation.phase_elapsed_time}
          startTime={new Date(automation.start_time * 1000).toLocaleString()}
        />
      </Grid>

      <Grid item xs={12} sm={3} md={3}>
        <AutomationFeedRate
          sx={{ height: '100%' }}
          feedRate={automation.feed_rate}
          feedRateSet={automation.settings.feed_rate}
          color={automation.feed_rate >= automation.settings.feed_rate - 10 ? 'success': 'warning'}
        />
      </Grid>

      <Grid item xs={12} sm={6} md={6}>
        <AutomationFeedProgress
          sx={{ height: '100%' }}
          percentage={automation.phase_percentage}
          feedDelivered={automation.feed_delivered}
          feedLimit={automation.settings.feed_limit}
          color={automation.feed_delivered >= automation.settings.feed_limit ? 'success': 'warning'}
        />
      </Grid>

      <Grid item xs={12} sm={12} md={12}>
        <FeedConfigurationAccordion
          feedLimit={automation.settings.feed_limit}
          feedRate={automation.settings.feed_rate}
          timeLimit={automation.settings.time_limit}
          feedDelivered={automation.feed_delivered}
          feedString={automation.settings.feed_string}
        />
      </Grid>

      <Grid item xs={12} sm={12} md={12}>
        <AutomationControlBar
          phase={automation.phase}
          paused={automation.paused}
          epo={automation.epo}
        />
      </Grid>
    </>
  );

  const renderOtherPhasesComponents = () => (
    <>
      <Grid item xs={12} sm={3} md={4}>
        <AutomationFeedElapsedTime
          sx={{ height: '100%' }}
          phaseElapsedTime={automation.phase_elapsed_time}
          startTime={new Date(automation.start_time * 1000).toLocaleString()}
        />
      </Grid>

      <Grid item xs={12} sm={3} md={8}>
        <PhaseProgress
          sx={{ height: '100%' }}
          percentage={automation.phase_percentage}
          phase={automation.phase}
          phaseDescription={automation.phase_description}
        />
      </Grid>

      {/* Render FeedConfigurationAccordion only for 'main', 'setup', and 'preflight' phases */}
      {['setup', 'preflight'].includes(automation.phase) && (
        <Grid item xs={12} sm={12} md={12}>
          <FeedConfigurationAccordion
            feedLimit={automation.settings.feed_limit}
            feedRate={automation.settings.feed_rate}
            timeLimit={automation.settings.time_limit}
            feedDelivered={automation.feed_delivered}
            feedString={automation.settings.feed_string}
          />
        </Grid>
      )}

      <Grid item xs={12} sm={12} md={12}>
        <AutomationControlBar
          phase={automation.phase}
          paused={automation.paused}
          epo={automation.epo}
        />
      </Grid>
    </>
  );
  

  return (
    <>
      <Grid container rowSpacing={2} columnSpacing={{ xs: 1, sm: 1, md: 2 }}>
        {automation.phase === 'main' ? renderMainPhaseComponents() : renderOtherPhasesComponents()}
      </Grid>
    </>
  );
}

export default AutomationState;
