import React from 'react'
import django from 'django'

const translations = {
  choins: django.gettext('choins'),
  your_investment: django.gettext('Your investment')
}

export default class InvestedChoins extends React.Component {
  constructor (props) {
    super(props)

    this.state = {
      userChoins: this.props.userChoins,
      userHasChoins: this.props.userChoins !== null,
      userChoinsId: this.props.userChoinsId
    }
  }

  render () {
    return (
      <div className="rating">
        {this.state.userHasChoins && (
          <>
            {translations.your_investment}:
            {this.state.userChoins} <i className="fa fa-coins" aria-label={translations.your_investment} />
          </>
        )}
      </div>
    )
  }
}
