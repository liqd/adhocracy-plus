import React from 'react'
import django from 'django'

const translations = {
  choins: django.gettext('choins'),
  with_you_and: django.gettext('with you and'),
  the_idea_cost: django.gettext('The idea cost is'),
  you_paid: django.gettext('You paid'),
  no_accepted_ideas: django.gettext('No accepted ideas'),
  accepted_ideas: django.gettext('Accepted Ideas'),
  no_modules: django.gettext('No modules'),
  wallet: django.gettext('Wallet'),
  module: django.gettext('Module'),
  supported_ideas: django.gettext("Ideas You've Supported"),
  other_supporters: django.gettext('other supporters')
}

export default class ModuleList extends React.Component {
  constructor (props) {
    super(props)

    this.state = {
      userFairvoteModules: this.props.userFairvoteModules,
      userHasFvModules: this.props.userFairvoteModules !== null
    }
  }

  render () {
    const { userFairvoteModules } = this.state
    return (
      <div className="bg--light">
        <div className="row">
          <h2>{translations.supported_ideas}</h2>
          <div className="col-md-10 col-lg-8 offset-md-1 offset-lg-2">
            <h3>{translations.accepted_ideas}</h3>
            {userFairvoteModules
              ? (Object.values(userFairvoteModules).map((module) => (
                <div key={module.name} className="card">
                  <div className="list-item__stats">
                    <h3 className="u-first-heading">
                      {translations.module}: {module.name}
                    </h3>
                    <span className="list-item__comments is-read-only" title="Choins">
                      {translations.module} {translations.wallet} <i className="fa fa-coins" aria-label="Choins" />
                      {module.choins}
                    </span>
                  </div>
                  {module.ideas.length > 0
                    ? (
                      <ul>
                        {module.ideas.map((idea) => (
                          <li key={idea.id}>
                            <strong>{idea.name}</strong>
                            <p>{translations.the_idea_cost} {idea.goal}, {translations.with_you_and} {idea.supporters_count} {translations.other_supporters};
                              {translations.you_paid} {idea.choins} {translations.choins}
                            </p>
                          </li>
                        ))}
                      </ul>
                      )
                    : (<p>{translations.no_accepted_ideas}</p>)}
                </div>
                )))
              : (<p>{translations.no_modules}</p>)}
          </div>
        </div>
      </div>
    )
  }
}
