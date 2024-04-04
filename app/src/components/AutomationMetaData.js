import PropTypes from 'prop-types';
import PlaceIcon from '@mui/icons-material/Place';
import {
  Avatar,
  Box,
  Card,
  CardContent,
  Stack,
  SvgIcon,
  Typography
} from '@mui/material';

export const AutomationMetaData = (props) => {
  const { cage, cohort, feedType, sx, color } = props;


  return (
    <Card sx={sx}>
      <CardContent>
        <Stack
          alignItems="flex-start"
          direction="row"
          justifyContent="space-between"
          spacing={3}
        >
          <Stack spacing={1}>
            <Typography
              color="text.secondary"
              gutterBottom
              variant="overline"
            >
              Details
            </Typography>
            <Typography variant="h4" style={{textWrap: 'nowrap'}}>
              {cage}
            </Typography>
          </Stack>
          <Avatar
            sx={{
              backgroundColor: 'primary.main',
              height: 56,
              width: 56
            }}
          >
            <SvgIcon>
              <PlaceIcon />
            </SvgIcon>
          </Avatar>
        </Stack>
        
        <Box sx={{ pt: 1 }}>
          <Typography variant="caption" color="textSecondary">
            Cohort: {' '}
            <Typography component="span" variant="caption" sx={{ color: `${color || 'primary'}.main` }}>
              {cohort}
            </Typography>{' '}
          </Typography>
        </Box>
        <Typography variant="caption" color="textSecondary">
          Feed type: {' '}
          <Typography component="span" variant="caption" sx={{ color: `${color || 'primary'}.main` }}>
            {feedType.formula}
          </Typography>{' '}
        </Typography>
      </CardContent>
    </Card>
  );
};

AutomationMetaData.propTypes = {
  cage: PropTypes.string.isRequired,
  cohort: PropTypes.string.isRequired,
  feedType: PropTypes.object.isRequired,
  sx: PropTypes.object,
  color: PropTypes.string
};

AutomationMetaData.defaultProps = {
  color: 'primary'
};
