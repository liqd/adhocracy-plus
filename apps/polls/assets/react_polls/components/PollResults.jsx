// PollResult.jsx - Simplified version
import React, { useState, useCallback, useMemo } from 'react'
import Slider from 'react-slick'
import django from 'django'
import { ChoiceRow } from './ChoiceRow'
import QuestionImage from 'adhocracy4/adhocracy4/polls/static/PollDetail/QuestionImage'

const SliderArrow = ({ className, style, onClick, currentSlide, slideCount }) => {
  const isPrev = className.includes('slick-prev')
  const disabled = isPrev
    ? currentSlide === 0
    : currentSlide === slideCount - 1

  const label = isPrev
    ? django.gettext('Previous answer')
    : django.gettext('Next answer')

  return (
    <button
      type="button"
      className={className}
      style={style}
      onClick={disabled ? null : onClick}
      aria-label={label}
      aria-disabled={disabled}
      disabled={disabled}
    />
  )
}

const OtherAnswersSection = ({ otherAnswers, isUserAnswer, showOtherAnswers, onToggle }) => {
  const settings = {
    arrows: true,
    speed: 500,
    slidesToShow: 1,
    slidesToScroll: 1,
    className: 'poll-slider',
    infinite: false,
    centerMode: true,
    centerPadding: '0px',
    prevArrow: <SliderArrow />,
    nextArrow: <SliderArrow />
  }

  if (!otherAnswers?.length) return null

  return (
    <div className="poll-result-other-section">
      <button
        type="button"
        className="btn poll__btn--link"
        onClick={onToggle}
      >
        {showOtherAnswers ? django.gettext('Hide other answers') : django.gettext('Show other answers')}
      </button>

      {showOtherAnswers && (
        <div className="poll-result-other-section__slider">
          <Slider {...settings}>
            {otherAnswers.map((slide, index) => (
              <div
                className="poll-slider__item"
                key={slide.id || index}
                role="group"
                aria-label={django.interpolate(
                  django.gettext('Answer %(current)s of %(total)s'),
                  { current: index + 1, total: otherAnswers.length },
                  true
                )}
              >
                <div className="poll-slider__answer">
                  {isUserAnswer(slide) && (
                    <i className="fas fa-check-circle" aria-label={django.gettext('Your answer')} />
                  )}
                  <span>{slide.answer}</span>
                </div>
                <div className="poll-slider__count">
                  {index + 1}/{otherAnswers.length}
                </div>
              </div>
            ))}
          </Slider>
        </div>
      )}
    </div>
  )
}

const PollResult = ({ question }) => {
  const [showOtherAnswers, setShowOtherAnswers] = useState(false)

  const userAnswerId = useMemo(() => {
    return question.is_open
      ? question.userAnswer
      : question.other_choice_user_answer
  }, [question])

  const isUserAnswer = useCallback((slide) => {
    const matchedId = question.is_open
      ? slide.id === userAnswerId
      : slide.vote_id === userAnswerId
    return !!matchedId
  }, [question.is_open, userAnswerId])

  const handleToggleOtherAnswers = useCallback(() => {
    setShowOtherAnswers(prev => !prev)
  }, [])

  const getHelpText = useMemo(() => {
    if (question.is_confidential) {
      const total = question.is_open ? question.totalAnswerCount : question.totalVoteCount
      return django.interpolate(
        django.ngettext('%s response submitted', '%s responses submitted', total),
        [total]
      )
    }

    if (question.is_open) {
      const total = question.totalAnswerCount
      return total >= 1
        ? django.interpolate(django.ngettext('1 person has answered.', '%s people have answered.', total), [total])
        : django.gettext('no one has answered this question')
    }

    const total = question.totalVoteCount
    const totalMulti = question.totalVoteCountMulti

    if (question.multiple_choice) {
      const participantText = total === 1 && totalMulti === 1
        ? django.gettext('%s participant gave 1 answer.')
        : django.ngettext('%s participant gave %s answers.', '%s participants gave %s answers.', total)

      return django.interpolate(
        participantText + django.gettext(' For multiple choice questions the percentages may add up to more than 100%.'),
        [total, totalMulti]
      )
    }

    return django.interpolate(
      django.ngettext('1 person has answered.', '%s people have answered.', total),
      [total]
    )
  }, [question])

  // Confidential question view
  if (question.is_confidential) {
    return (
      <div className="poll poll--result poll--confidential">
        <h2>{question.label}</h2>
        {question.image_url && <QuestionImage imageUrl={question.image_url} alt={question.image_alt_text || question.label} />}
        <div className="a4-muted">{getHelpText}</div>
        <p className="poll__confidential-notice">
          <i className="fa fa-lock" aria-hidden="true" />{' '}
          {django.gettext('Answers to this question will be visible only to the initiators of this project.')}
        </p>
      </div>
    )
  }

  const totalVotes = question.totalVoteCount

  return (
    <div className="poll poll--result">
      <h2>{question.label}</h2>
      {question.image_url && <QuestionImage imageUrl={question.image_url} alt={question.image_alt_text || question.label} />}

      <div className="poll__rows">
        {/* Non-open questions - reuse ChoiceRow */}
        {!question.is_open && question.choices.map(choice => {
          const isChosen = question.userChoices.includes(choice.id)
          const percent = totalVotes === 0 ? 0 : Math.round((choice.count / totalVotes) * 100)

          return (
            <div key={choice.id}>
              <ChoiceRow
                choice={choice}
                checked={isChosen}
                type={question.multiple_choice ? 'checkbox' : 'radio'}
                isResult
                percent={percent}
                disabled
              />

              {/* Other answers section */}
              {choice.is_other_choice && (
                <OtherAnswersSection
                  otherAnswers={question.other_choice_answers}
                  isUserAnswer={isUserAnswer}
                  showOtherAnswers={showOtherAnswers}
                  onToggle={handleToggleOtherAnswers}
                />
              )}
            </div>
          )
        })}

        {/* Open questions */}
        {question.is_open && question.answers?.length > 0 && (
          <div className="poll-slider__container">
            <Slider {...{
              arrows: true,
              speed: 500,
              slidesToShow: 1,
              slidesToScroll: 1,
              className: 'poll-slider',
              infinite: false,
              centerMode: true,
              centerPadding: '0px',
              prevArrow: <SliderArrow />,
              nextArrow: <SliderArrow />
            }}
            >
              {question.answers.map((slide, index) => (
                <div className="poll-slider__item" key={slide.id || index}>
                  <div className="poll-slider__answer">
                    {isUserAnswer(slide) && (
                      <i className="fas fa-check-circle" aria-label={django.gettext('Your answer')} />
                    )}
                    <span>{slide.answer}</span>
                  </div>
                  <div className="poll-slider__count">
                    {index + 1}/{question.answers.length}
                  </div>
                </div>
              ))}
            </Slider>
          </div>
        )}

        {/* Help text */}
        <div className="a4-muted">{getHelpText}</div>
      </div>
    </div>
  )
}

export default PollResult
