import React from 'react';
import ReactDOM from 'react-dom';
import { Router, Route, IndexRoute, browserHistory } from 'react-router';
import { PageContainer } from './components/PageContainer';
import { RosterContainer } from './components/RosterContainer';

require('scss/main.scss');

const Root = () => (
  <Router history={browserHistory}>
    <Route path="/">
      <IndexRoute component={PageContainer} />
      <Route path="/roster" component={RosterContainer} />
    </Route>
  </Router>
);

document.addEventListener('DOMContentLoaded', () => {
  ReactDOM.render(<Root />, document.getElementById('react-root'));
});
