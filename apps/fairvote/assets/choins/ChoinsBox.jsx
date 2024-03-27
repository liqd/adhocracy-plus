import React from 'react'
import django from 'django'

const translations = {
  choins: django.gettext('choins'),
  wallet: django.gettext('Your wallet: ')
}

export default class ChoinsBox extends React.Component {
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
            <span>{translations.wallet}</span>
            {this.state.userChoins}
          </>
        )}
      </div>
    )
  }
}
