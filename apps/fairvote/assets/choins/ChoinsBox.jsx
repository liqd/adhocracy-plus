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
      userChoins: parseFloat(this.props.userChoins).toFixed(2),
      userHasChoins: this.props.userChoins !== null,
      userChoinsId: this.props.userChoinsId
    }
    console.log(typeof this.props.userChoins)
  }

  render () {
    return (
      <div className="rating">
        {this.state.userHasChoins && (
          <>
            <span>{translations.wallet}</span>
            {this.state.userChoins} Choins
          </>
        )}
      </div>
    )
  }
}
