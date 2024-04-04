import React from 'react';

import {
  TextField,
  Grid,
  InputAdornment,
  Tooltip
} from '@mui/material';

import MedicationIcon from '@mui/icons-material/Medication';

export default class FeedStringMeta extends React.Component {

    constructor(props) {
        super(props);
        this.state = {};
    }

    render() {
      const { feedString } = this.props;

      return (
        <Grid item xs={12} sm={12} md={12}>
          <Grid container columnSpacing={1}>
            <Grid item xs={4}>
              <TextField
                  fullWidth
                  disabled
                  id="filled-disabled"
                  label="Cage"
                  value={feedString.cage}
                />
            </Grid>
            <Grid item xs={4}>
              <TextField
                fullWidth
                disabled
                id="filled-disabled"
                label="Cohort"
                value={feedString.cohort}
              />
            </Grid>
            <Grid item xs={4}>
              <TextField
                fullWidth
                disabled
                id="filled-disabled"
                label={feedString.diet.formula}
                value={`${feedString.diet.brand} ${feedString.diet.diameter}`}
                InputProps={{
                  startAdornment: feedString.diet.medicated ? (
                    <InputAdornment position="start">
                      <Tooltip title="Medicated">
                        <MedicationIcon />
                      </Tooltip>
                    </InputAdornment>
                  ) : null,
                }}
              />
            </Grid>
          </Grid>
        </Grid>
      );
    }

}