import React from 'react';
import {
  Grid,
} from '@mui/material';

import { AutomationFeedElapsedTime } from './AutomationFeedElapsedTime';
import { AutomationFeedProgress } from './AutomationFeedProgress';
import { AutomationControlBar } from './AutomationControlBar';
import { AutomationMetaData } from './AutomationMetaData';


function AutomationReport(props) {
  const { automation } = props;

  return (
    <>
      <Grid container rowSpacing={2} columnSpacing={{ xs: 1, sm: 1, md: 2 }}>

        <Grid item xs={12} sm={4} md={3}>
          <AutomationMetaData
            sx={{ height: '100%' }}
            cage={automation.settings.feed_string.cage}
            cohort={automation.settings.feed_string.cohort}
            feedType={automation.settings.feed_string.diet}
          />
        </Grid>

        <Grid item xs={12} sm={4} md={3}>
          <AutomationFeedElapsedTime
            sx={{ height: '100%' }}
            phaseElapsedTime={automation.elapsed_time}
            startTime={new Date(automation.start_time * 1000).toLocaleString()}
            endTime={new Date(automation.end_time * 1000).toLocaleString()}
          />
        </Grid>

        <Grid item xs={12} sm={8} md={6}>
          <AutomationFeedProgress
            title={'Feed Report'}
            sx={{ height: '100%' }}
            percentage={Math.round( (automation.feed_delivered / automation.settings.feed_limit) * 100)}
            feedDelivered={automation.feed_delivered}
            feedLimit={automation.settings.feed_limit}
            color={automation.feed_delivered >= automation.settings.feed_limit ? 'success': 'warning'}
          />
        </Grid>

        <Grid item xs={12} sm={12} md={12}>
          <AutomationControlBar
            phase={automation.phase}
            paused={automation.paused}
            epo={automation.epo}
          />
        </Grid>
        
      </Grid>
    </>
  );
}

export default AutomationReport;